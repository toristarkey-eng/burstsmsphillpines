import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab'
sys.path.insert(0, str(SKILL))
from runtime.renderer import Campaign, Hold, Canvas, PALETTE, render, catalog, load_locks


def campaign(template='recognition', fmt='portrait', photo=None):
    if photo is None:
        photo = 'commercial-team' if template == 'team-coffee' else 'workplace-portrait' if template in ['people-first', 'customer-updates'] else None
    return Campaign(template_id=template, format=fmt, headline='Make every message count.', accent='Stay connected.', supporting='Explore messaging for your business.', primary_text='Talk to Burst SMS Philippines about messaging for your business.', photo_id=photo)


def inspection(report):
    checks = report['inspection_required']
    return {'png_sha256': report['png_sha256'], 'campaign_sha256': report['campaign_sha256'], 'checks': {key: True for key in checks},
            'notes': {key: 'Test fixture inspection only; not publication or actual owner approval.' for key in checks}}


class RendererTests(unittest.TestCase):
    def test_every_template_and_export_size_is_deterministic(self):
        for template in catalog()['templates']:
            for fmt in ('square', 'portrait'):
                with self.subTest(template=template, format=fmt):
                    png, report = render(campaign(template, fmt))
                    again, _ = render(campaign(template, fmt))
                    self.assertEqual(png, again)
                    self.assertEqual(Image.open(io.BytesIO(png)).size, (1080, 1080 if fmt == 'square' else 1350))
                    self.assertTrue(all(report['checks'].values()))
                    self.assertEqual(report['delivery_status'], 'INSPECTION_REQUIRED')
                    self.assertEqual(report['destination'], 'https://burstsms.com.ph/')

    def test_explicit_formats_recompose_preserve_logo_and_dimensions(self):
        requests = [('landscape', None, (1200,628)), ('story', None, (1080,1920)),
                    ('custom', [1200,800], (1200,800)), ('custom', [1200,600], (1200,600)),
                    ('custom', [600,1200], (600,1200))]
        master=Image.open(SKILL/'assets/burst-sms-logo.png').convert('RGB')
        for fmt, dims, size in requests:
            for template in catalog()['templates']:
                for strip in ('top','bottom'):
                    with self.subTest(format=fmt, dimensions=dims, template=template, strip=strip):
                        brief=campaign(template,'portrait' if fmt=='custom' else fmt).model_copy(update={'format':fmt, **{'dimensions':dims,'brand_strip':strip,
                            'headline':'Stay connected.', 'accent':'Business messaging.',
                            'supporting':'Talk to our team.', 'message':'Order ready. Thank you!' if template in ('recognition','customer-updates') else ''}})
                        png,report=render(brief)
                        image=Image.open(io.BytesIO(png)).convert('RGB')
                        self.assertEqual(image.size,size)
                        self.assertEqual(report['dimensions'],list(size))
                        x,y,w,h=report['logo_box']
                        expected=master.resize((w,h),Image.Resampling.LANCZOS)
                        self.assertIsNone(ImageChops.difference(image.crop((x,y,x+w,y+h)),expected).getbbox())
                        self.assertAlmostEqual(w/h,master.width/master.height,delta=0.03)
                        self.assertTrue(all(report['checks'].values()))
                        for text in report['text_checks']:
                            tx,ty,tw,th=text['box']
                            self.assertGreaterEqual(min(tx,ty),0)
                            self.assertLessEqual(tx+tw,size[0]+1)
                            self.assertLessEqual(ty+text['used_height'],size[1]+1)
        self.assertEqual(campaign().format,'portrait')
        for updates in ({'format':'custom'}, {'format':'custom','dimensions':[1600,200]},
                        {'format':'custom','dimensions':[4097,3000]}, {'format':'custom','dimensions':[600.0,600]},
                        {'format':'square','dimensions':[1200,1200]}):
            with self.assertRaises(Hold): render(campaign().model_copy(update=updates))

    def test_all_registered_photos_and_ctas_in_both_sizes(self):
        config = catalog()
        for photo_id, photo in config['photos'].items():
            if photo.get('requires_crop'): continue
            for template in photo['templates']:
                for fmt in config['formats']:
                    with self.subTest(photo=photo_id, template=template, format=fmt):
                        _, report = render(campaign(template, fmt, photo_id))
                        self.assertEqual(report['photography'], photo)
        for cta in config['ctas']:
            for fmt in config['formats']:
                _, report = render(campaign(fmt=fmt).model_copy(update={'cta': cta}))
                self.assertIn(cta, report['channel_copy'])

    def test_logo_pixels_proportions_and_master_bytes_are_preserved(self):
        logo = Image.open(SKILL/'assets/burst-sms-logo.png').convert('RGB')
        expected = logo.resize((logo.width*2, logo.height*2), Image.Resampling.LANCZOS)
        png, report = render(campaign())
        image = Image.open(io.BytesIO(png)).convert('RGB')
        self.assertIsNone(ImageChops.difference(image.crop((56,15,56+expected.width,15+expected.height)),expected).getbbox())
        self.assertEqual(report['logo_sha256'],'3b6bb8131d6ce1bf81d7f2481d8b3159058c8e71e87e0d6b5f1582efde3341f2')

    def test_all_adaptive_variants_preserve_protected_regions(self):
        for template in catalog()['templates']:
            for fmt in ('square', 'portrait'):
                for strip in ('top', 'bottom'):
                    for composition in ('auto', 'side-by-side', 'text-first', 'image-first'):
                        _,report=render(campaign(template,fmt).model_copy(update={'brand_strip':strip,'composition':composition}))
                        height=report['dimensions'][1]
                        for check in report['text_checks']:
                            x,y,w,h=check['box']
                            self.assertGreaterEqual(y,150 if strip=='top' else 0)
                            self.assertLessEqual(y+check['used_height'],height if strip=='top' else height-150)
                        self.assertTrue(all(report['checks'].values()))

    def test_auto_body_balances_copy_and_phone_with_a_real_message(self):
        png, report = render(campaign(fmt='square').model_copy(update={
            'headline': 'Your next business move?', 'accent': 'White Label SMS.',
            'supporting': "Looking to offer SMS under your own brand? Let's talk.",
            'message': 'Your order is ready for collection. Thank you!', 'image_position': 'right'}))
        self.assertEqual(report['body_layout'], 'side-by-side')
        headline = report['text_checks'][0]
        message = next(t for t in report['text_checks'] if t['text'] == report['phone_message'])
        self.assertLess(headline['box'][0]+headline['box'][2], message['box'][0])
        self.assertTrue(report['checks']['message_visible'])
        # Check the actual rendered message card, not just a declared flag.
        image=Image.open(io.BytesIO(png)).convert('RGB')
        x,y,w,h=message['box']
        self.assertIn((0,42,102), set(image.crop((x,y,x+w,y+message['used_height'])).get_flattened_data()))
        for placeholder in ('Your brand here','Your message here','Lorem ipsum'):
            with self.assertRaises(Hold): render(campaign().model_copy(update={'message':placeholder}))

    def test_phone_views_sender_and_bubble_are_measured_not_placeholders(self):
        for fmt in ('square','landscape','story'):
            for view in ('auto','full','detail'):
                if fmt=='landscape' and view=='full':
                    with self.assertRaisesRegex(Hold,'Full phone view is too small'): render(campaign(fmt=fmt).model_copy(update={'phone_view':view}))
                    continue
                png,report=render(campaign(fmt=fmt).model_copy(update={'phone_view':view,'sender_name':'ACME SHOP','message':'Your order is ready.'}))
                check=report['phone_check']
                if check['device_dimensions'] is not None:
                    self.assertAlmostEqual(check['device_dimensions'][0]/check['device_dimensions'][1],0.5,delta=0.003)
                if view=='auto': self.assertIn(check['view'],('full','card'))
                self.assertEqual(check['sender_header'],'ACME SHOP')
                self.assertTrue(check['message_bubble'] and check['message_fully_visible'])
                image=Image.open(io.BytesIO(png)).convert('RGB')
                self.assertTrue(any(t['text']=='ACME SHOP' for t in report['text_checks']))
                message=next(t for t in report['text_checks'] if t['text']=='Your order is ready.')
                x,y,w,h=message['box']
                pixels=set(image.crop((x,y,x+w,y+message['used_height'])).get_flattened_data())
                self.assertIn((0,42,102),pixels)
                self.assertIn((244,245,255),pixels)
        for sender in ('YOUR BRAND','OVERLONGSENDER','evil.example','<brand>'):
            with self.assertRaises(Hold): render(campaign().model_copy(update={'sender_name':sender}))

    def test_full_device_default_and_cover_photo_fill(self):
        for fmt in ('square','portrait','landscape','story'):
            _,r=render(campaign(fmt=fmt))
            phone=r['phone_check']
            if phone['view']=='full':
                self.assertEqual(phone['visible_frame'][3],phone['device_dimensions'][1])
            else: self.assertEqual(phone['view'],'card')
            self.assertFalse(phone['unintended_device_crop'])
            _,r=render(campaign('people-first',fmt).model_copy(update={'composition':'hero','headline':'Stay connected.','accent':'','supporting':''}))
            photo=r['photo_checks'][0]
            self.assertEqual(photo['photo_fit'],'cover')
            self.assertTrue(photo['additional_crop_inspection_required'])
            self.assertAlmostEqual(photo['frame'][2],photo['region'][2],delta=3)
            self.assertAlmostEqual(photo['frame'][3],photo['region'][3],delta=3)
            self.assertLessEqual(photo['effective_crop'][2],photo['registered_crop'][2])
            self.assertLessEqual(photo['effective_crop'][3],photo['registered_crop'][3])

    def test_navy_heading_with_photography_has_visible_contrast_and_panel(self):
        for fmt in ('square','portrait','landscape','story'):
            for strip in ('top','bottom'):
                png,r=render(campaign('people-first',fmt).model_copy(update={'heading_style':'navy','composition':'hero',
                    'brand_strip':strip,'headline':'Keep customers','accent':'in the loop.','supporting':''}))
                self.assertEqual(r['heading_style'],'navy')
                self.assertTrue(r['photo_checks'])
                image=Image.open(io.BytesIO(png)).convert('RGB')
                x,y,w,h=r['heading_region']
                self.assertEqual(image.getpixel((image.width-2,y+5)),(0,42,102))
                heading=r['text_checks'][0];tx,ty,tw,th=heading['box']
                self.assertIn((255,255,255),set(image.crop((tx,ty,tx+tw,ty+heading['used_height'])).get_flattened_data()))
                self.assertTrue(r['checks']['text_contrast'])

    def test_photo_and_sms_can_share_body_beside_without_overlap(self):
        for strip in ('top','bottom'):
            png,r=render(campaign('recognition','square','retail-messaging').model_copy(update={
                'heading_style':'navy','composition':'hero','message_placement':'beside','brand_strip':strip,
                'headline':'Keep customers informed.','accent':'','supporting':'',
                'sender_name':'ACME SHOP','message':'Your order is ready to collect. Thank you!'}))
            self.assertEqual(r['message_placement'],'beside')
            x,y,w,h=r['photo_checks'][0]['frame']; mx,my,mw,mh=r['message_card']
            self.assertLessEqual(x+w,mx)
            self.assertGreaterEqual(my,y)
            self.assertLessEqual(my+mh,y+h+2)
            self.assertTrue(all(r['checks'].values()))

    def test_dynamic_photo_masks_and_source_scene_selection(self):
        for treatment in ('rounded','circle','cutout'):
            _,report=render(campaign('people-first','square','collaborating-colleagues').model_copy(update={'image_treatment':treatment}))
            check=report['photo_checks'][0]
            self.assertEqual(check['requested_treatment'],treatment)
            self.assertEqual(check['image_treatment'],'panel' if treatment=='cutout' else treatment)
            self.assertEqual(check['mask_has_transparency'],treatment!='cutout')
            if treatment=='cutout': self.assertIn('retained original',check['cutout_fallback'])
            self.assertTrue(check['subject_and_edges_inspection_required'])
        _,report=render(campaign('people-first','portrait','source-collaborative').model_copy(update={
            'photo_crop':[1158,3,1530,330], 'photo_description':'Illustrative colleagues at a laptop', 'image_treatment':'cutout'}))
        self.assertEqual(report['photography']['crop'],[1158,3,1530,330])
        for update in ({'photo_id':'source-collaborative'}, {'photo_crop':[-1,0,100,100]},
                       {'photo_crop':[0,0,99999,99999]}, {'image_treatment':'arbitrary'}):
            with self.assertRaises(Hold): render(campaign('people-first').model_copy(update=update))

    def test_cta_brand_terms_and_photo_treatments_across_formats(self):
        sizes=[('square',None),('portrait',None),('landscape',None),('story',None),('custom',[1200,800])]
        for fmt,dims in sizes:
            for strip in ('top','bottom'):
                for treatment in ('panel','rounded','circle','cutout'):
                    brief=campaign('customer-updates').model_copy(update={'format':fmt,'dimensions':dims,'brand_strip':strip,
                        'image_treatment':treatment,'headline':'Stay connected.','accent':'Business messaging.',
                        'supporting':'Talk to our team.','message':'Your order is ready.',
                        'offer_terms':'Eligibility applies. Confirm details with our team.'})
                    with self.subTest(format=fmt,strip=strip,treatment=treatment):
                        png,r=render(brief)
                        image=Image.open(io.BytesIO(png)).convert('RGB')
                        bx,by,bw,bh=r['brand_region'];cx,cy,cw,ch=r['cta_region']
                        button=r['cta_button']; terms=r['terms_box']
                        self.assertLessEqual(cy+ch,by if strip=='bottom' else image.height)
                        self.assertLessEqual(terms[1]+terms[3],cy+ch+1)
                        self.assertLessEqual(button[1]+button[3],cy+ch+1)
                        self.assertEqual(r['cta_alignment'],'same-line')
                        website=r['website_box']
                        self.assertGreater(website[0],button[0]+button[2])
                        self.assertAlmostEqual(website[1],button[1]+(16 if r['layout_dimensions'][1]<900 else 22)*image.width/1080,delta=2)
                        if strip=='bottom':
                            self.assertAlmostEqual(cy+ch,by,delta=1)
                            self.assertEqual(image.getpixel((image.width-2,cy+4)),(244,245,255))
                        else: self.assertEqual(image.getpixel((image.width-2,cy+4)),(255,255,255))
                        for text in r['text_checks']:
                            self.assertTrue(text['box'][1]+text['used_height']<=by or text['box'][1]>=by+bh)
                        frame=r['photo_checks'][0]['frame']; card=r['message_card']
                        self.assertLessEqual(frame[1]+frame[3],card[1])
                        self.assertLessEqual(card[1]+card[3],cy)
                        self.assertTrue(all(r['checks'].values()))
                        self.assertIn('photo_edges',r['inspection_required'])
        # A requested RGB cutout must preserve exactly the original-background raster.
        original,_=render(campaign('people-first').model_copy(update={'image_treatment':'panel'}))
        fallback,r=render(campaign('people-first').model_copy(update={'image_treatment':'cutout'}))
        self.assertEqual(original,fallback)
        self.assertIsNotNone(r['photo_checks'][0]['cutout_fallback'])

    def test_masks_backdrops_and_native_alpha_preserve_bounds_and_white_subjects(self):
        for treatment in ('rounded','circle'):
            for backing in ('none','cyan-ellipse'):
                c=Canvas((300,300));before=c.image.copy()
                c.photo(catalog()['photos']['workplace-portrait'],(40,40,220,220),treatment=treatment,backdrop=backing)
                x,y,w,h=c.photo_checks[0]['frame']
                for region in ((0,0,300,y),(0,y+h,300,300),(0,0,x,300),(x+w,0,300,300)):
                    self.assertIsNone(ImageChops.difference(c.image.crop(region),before.crop(region)).getbbox())
                # Rounded/ellipse corner outside the shared mask cannot contain a cyan ellipse sliver.
                self.assertEqual(c.image.getpixel((x,y)),before.getpixel((x,y)))
        source=Image.new('RGBA',(100,100),(255,255,255,0))
        from PIL import ImageDraw
        ImageDraw.Draw(source).rectangle((20,10,80,99),fill=(255,255,255,255))
        ImageDraw.Draw(source).rectangle((40,40,60,70),fill=(0,42,102,255))
        with patch('runtime.renderer.Image.open',return_value=source):
            c=Canvas((140,140));c.photo({'file':'registered-alpha.png','crop':[0,0,100,100],'approved_subject_alpha':True},(20,20,100,100),treatment='cutout')
        self.assertEqual(c.image.getpixel((45,45)),(255,255,255))
        self.assertEqual(c.image.getpixel((70,75)),(0,42,102))
        self.assertEqual(c.image.getpixel((25,25)),(244,245,255))
        self.assertIsNone(c.photo_checks[0]['cutout_fallback'])

    def test_adaptive_copy_uses_compact_measured_spacing(self):
        _, report = render(campaign(fmt='square').model_copy(update={
            'headline': 'Keep customers', 'accent': 'informed.', 'supporting': 'Discuss customer updates with our team.', 'composition': 'text-first'}))
        heading, accent, supporting = report['text_checks'][:3]
        self.assertEqual(accent['box'][1] - (heading['box'][1] + heading['used_height']), 12)
        self.assertEqual(supporting['box'][1] - (accent['box'][1] + accent['used_height']), 28)
        self.assertLess(accent['box'][1], 330)

    def test_photo_frames_fill_and_preserve_registered_panels(self):
        for fmt in ('square', 'portrait'):
            for placement in ('left', 'centre', 'right'):
                _, report = render(campaign('people-first', fmt, 'collaborating-colleagues').model_copy(update={'image_position': placement}))
                photo = report['photo_checks'][0]
                x,y,w,h = photo['frame']; rx,ry,rw,rh = photo['region']
                self.assertTrue(rx <= x and ry <= y and x+w <= rx+rw and y+h <= ry+rh)
                crop = photo['registered_crop']
                self.assertAlmostEqual(w/h, (crop[2]-crop[0])/(crop[3]-crop[1]), delta=0.01)
                self.assertTrue(photo['frame_filled'] and photo['complete_panel_preserved'])

    def test_bottom_strip_preserves_logo_and_image_first_reorders_sections(self):
        original = Image.open(SKILL/'assets/burst-sms-logo.png').convert('RGB')
        expected = original.resize((original.width*2, original.height*2), Image.Resampling.LANCZOS)
        for fmt in ('square', 'portrait'):
            png, report = render(campaign('people-first', fmt).model_copy(update={'brand_strip': 'bottom', 'composition': 'image-first'}))
            image=Image.open(io.BytesIO(png)); x,y,w,h=report['logo_box']
            self.assertIsNone(ImageChops.difference(image.crop((x,y,x+w,y+h)), expected).getbbox())
            frame=report['photo_checks'][0]['frame']
            self.assertLess(frame[1]+frame[3], report['text_checks'][0]['box'][1])
            self.assertGreater(y, image.height-150)

    def test_recognition_accepts_only_registered_illustrative_photography(self):
        _, report = render(campaign(fmt='square', photo='retail-messaging'))
        self.assertTrue(report['photo_checks'][0]['complete_panel_preserved'])
        with self.assertRaises(Hold): render(campaign(photo='commercial-team'))
        _, report = render(campaign(fmt='square',photo='retail-messaging').model_copy(update={'message':'Your order is ready.','sender_name':'ACME SHOP'}))
        self.assertEqual(report['phone_message'],'Your order is ready.')
        self.assertTrue(any(t['text']=='ACME SHOP' for t in report['text_checks']))
        self.assertTrue(any(t['text']=='Your order is ready.' for t in report['text_checks']))
        with self.assertRaises(Hold): render(campaign(photo='retail-messaging').model_copy(update={'phone_view':'full'}))
        for key,value in [('brand_strip','middle'),('composition','freeform'),('image_position',[5,10])]:
            with self.assertRaises(Hold): render(campaign().model_copy(update={key:value}))

    def test_brand_overrides_paths_links_dimensions_and_extra_fields_are_rejected(self):
        for name, value in [('colour','#ff00ff'),('logo_path','/tmp/logo.png'),('font','Arial'),('dimensions',[400,400]),('html','<script>'),('destination','https://evil.example'),('approved',True),('skip_validation',True)]:
            with self.subTest(field=name), self.assertRaises(ValidationError):
                Campaign.model_validate({**campaign().model_dump(),name:value})
        for update in [{'photo_id':'../../etc/passwd'}, {'photo_id':'unregistered'}, {'template_id':'arbitrary'}, {'format':'unsupported-banner'}, {'cta':'Visit another site'}, {'headline':'Use Kudosity'}, {'headline':'Guaranteed best results'}, {'headline':'Go to evil.example'}, {'headline':'Try 192.0.2.1'}, {'headline':'Hello\u202eevil'}]:
            with self.subTest(update=update), self.assertRaises(Hold):
                render(campaign().model_copy(update=update))

    def test_overflow_and_actual_background_contrast_block_render(self):
        with self.assertRaises(Hold): render(campaign().model_copy(update={'headline':'W'*65}))
        canvas = Canvas((300,120)); canvas.text('Example',(5,5,280,80),32,'white')
        canvas.draw.rectangle((0,0,300,120),fill=PALETTE['cyan'])
        with self.assertRaises(Hold): canvas.finish_text()
        canvas = Canvas((300,120)); canvas.text('Example',(5,5,280,80),32); canvas.text('Example',(5,5,280,80),32)
        with self.assertRaises(Hold): canvas.finish_text()
        with self.assertRaises(Hold): Canvas((300,120)).text('Example',(-1,0,100,80),32)

    def test_photo_use_and_message_fields_are_locked(self):
        with self.assertRaises(Hold): render(campaign('team-coffee').model_copy(update={'photo_id':'workplace-portrait'}))
        with self.assertRaises(Hold): render(campaign('people-first').model_copy(update={'photo_id':None}))
        with self.assertRaises(Hold): render(campaign('bold-statement').model_copy(update={'message':'Wrong template'}))


class StandaloneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.skill = self.base/'installed-skill'
        shutil.copytree(SKILL,self.skill,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        self.cwd = self.base/'unrelated'; self.cwd.mkdir()
        self.brief = self.base/'campaign.json'; self.brief.write_text(campaign().model_dump_json())
        self.output = self.base/'private-render'

    def tearDown(self): self.temp.cleanup()

    def run_cli(self,*args,surface='work',python_flags=('-I',)):
        environment = os.environ.copy()
        environment.pop('PYTHONPATH',None); environment.pop('BURST_SMS_PH_REPO_BASE_URL',None)
        guard = "import socket,runpy,sys; socket.socket=lambda *a,**k: (_ for _ in ()).throw(AssertionError('Network access forbidden')); sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
        return subprocess.run([sys.executable,*python_flags,'-c',guard,str(self.skill/'scripts/render_creative.py'),'--surface',surface,*map(str,args)],cwd=self.cwd,env=environment,capture_output=True,text=True)

    def prepare(self):
        result = self.run_cli('render','--brief',self.brief,'--output-dir',self.output)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(json.loads(result.stdout)['image_ready_for_delivery'])
        report = json.loads((self.output/'render-report.json').read_text())
        self.review = self.base/'inspection.json'; self.review.write_text(json.dumps(inspection(report)))
        return report

    def validate(self): return self.run_cli('validate','--directory',self.output,'--inspection',self.review)

    def test_copied_skill_runs_independently_and_delivers_only_after_inspection(self):
        result = self.run_cli('preflight'); self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn(str(ROOT),result.stdout)
        self.prepare(); self.assertFalse((self.output/'delivery-validation.json').exists())
        result = self.validate(); self.assertEqual(result.returncode,0,result.stderr)
        receipt = json.loads(result.stdout); self.assertEqual(receipt['status'],'PASSED')
        self.assertEqual(receipt['publication_status'],'NOT_PUBLISHED')
        self.assertTrue(receipt['image_ready_for_delivery'])
        self.assertEqual(hashlib.sha256((self.output/'artwork.png').read_bytes()).hexdigest(),receipt['png_sha256'])

    def test_ordinary_chat_holds_without_importing_dependencies_or_writing_artwork(self):
        result = self.run_cli('render','--brief',self.brief,'--output-dir',self.output,surface='chat',python_flags=('-I','-S'))
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Creative production requires Work',result.stderr)
        self.assertFalse(self.output.exists())

    def test_all_sizes_and_templates_work_from_copied_package(self):
        for template in catalog()['templates']:
            for fmt in ('square','portrait'):
                with self.subTest(template=template,format=fmt):
                    self.brief.write_text(campaign(template,fmt).model_dump_json())
                    target=self.base/(template+'-'+fmt)
                    result=self.run_cli('render','--brief',self.brief,'--output-dir',target)
                    self.assertEqual(result.returncode,0,result.stderr)
                    with Image.open(target/'artwork.png') as image:
                        self.assertEqual(image.size,(1080,1080 if fmt=='square' else 1350))

    def test_modified_logo_font_photo_tokens_code_or_messaging_blocks_preflight(self):
        files=['assets/burst-sms-logo.png','runtime/fonts/NotoSans-SemiBold.ttf','assets/burst-sms-ph-commercial-team.jpg','assets/tokens.json','runtime/renderer.py','references/messaging-library-brief.md']
        for relative in files:
            with self.subTest(file=relative):
                file=self.skill/relative; original=file.read_bytes()
                try:
                    file.write_bytes(original+b'\n# changed\n')
                    result=self.run_cli('preflight'); self.assertNotEqual(result.returncode,0)
                    self.assertIn('HOLD',result.stderr)
                finally: file.write_bytes(original)

    def test_missing_asset_or_lock_coverage_blocks_without_artifacts(self):
        path=self.skill/'runtime/fonts/NotoSans-Bold.ttf'; path.unlink()
        result=self.run_cli('render','--brief',self.brief,'--output-dir',self.output)
        self.assertNotEqual(result.returncode,0); self.assertFalse(self.output.exists())
        shutil.copy2(SKILL/'runtime/fonts/NotoSans-Bold.ttf',path)
        manifest=self.skill/'brand-integrity.json'; data=json.loads(manifest.read_text()); del data['files']['runtime/renderer.py']; manifest.write_text(json.dumps(data))
        self.assertNotEqual(self.run_cli('preflight').returncode,0)

    def test_failed_or_stale_inspection_never_delivers(self):
        report=self.prepare(); original=inspection(report)
        for change in ['false','string','missing','stale','empty-notes']:
            data=json.loads(json.dumps(original))
            if change=='false': data['checks']['copy_and_claims']=False
            elif change=='string': data['checks']['copy_and_claims']='true'
            elif change=='missing': del data['checks']['accessibility']
            elif change=='stale': data['png_sha256']='0'*64
            else: data['notes']['copy_and_claims']=''
            self.review.write_text(json.dumps(data)); result=self.validate()
            self.assertNotEqual(result.returncode,0); self.assertFalse((self.output/'delivery-validation.json').exists())

    def test_changed_artwork_copy_or_record_invalidates_passed_receipt(self):
        self.prepare()
        for name in ['artwork.png','recommended-copy.md','render-report.json']:
            self.assertEqual(self.validate().returncode,0)
            file=self.output/name; original=file.read_bytes()
            try:
                file.write_bytes(original+b'changed')
                result=self.validate(); self.assertNotEqual(result.returncode,0)
                self.assertFalse((self.output/'delivery-validation.json').exists())
            finally: file.write_bytes(original)

    def test_visual_edge_balance_or_cta_failure_overrides_technical_pass(self):
        self.prepare()
        original=json.loads(self.review.read_text())
        for key in ('photo_edges','body_balance','cta_and_terms','campaign_effectiveness'):
            self.review.write_text(json.dumps(original))
            self.assertEqual(self.validate().returncode,0)
            failed=json.loads(json.dumps(original)); failed['checks'][key]=False
            failed['notes'][key]='Actual visual check failed; do not deliver this artwork.'
            self.review.write_text(json.dumps(failed))
            self.assertNotEqual(self.validate().returncode,0)
            self.assertFalse((self.output/'delivery-validation.json').exists())

    def test_failed_package_preflight_invalidates_previous_delivery_receipt(self):
        self.prepare()
        self.assertEqual(self.validate().returncode, 0)
        path = self.skill/'assets/tokens.json'
        path.write_bytes(path.read_bytes() + b' ')
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.output/'delivery-validation.json').exists())

    def test_invalid_brief_duplicate_fields_and_oversized_input_leave_no_output(self):
        for body in [json.dumps({**campaign().model_dump(),'colour':'pink'}),'{"template_id":"recognition","template_id":"other"}', ' '*20000]:
            self.brief.write_text(body)
            result=self.run_cli('render','--brief',self.brief,'--output-dir',self.output)
            self.assertNotEqual(result.returncode,0); self.assertFalse(self.output.exists())

    def test_renderer_never_overwrites_existing_directories_or_installed_package(self):
        self.output.mkdir(); (self.output/'user-file').write_text('preserve me')
        result=self.run_cli('render','--brief',self.brief,'--output-dir',self.output)
        self.assertNotEqual(result.returncode,0); self.assertEqual((self.output/'user-file').read_text(),'preserve me')
        result=self.run_cli('render','--brief',self.brief,'--output-dir',self.skill/'output')
        self.assertNotEqual(result.returncode,0); self.assertFalse((self.skill/'output').exists())


if __name__=='__main__': unittest.main()
