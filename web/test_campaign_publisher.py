import json
from pathlib import Path
import tempfile
import unittest
from campaign_publisher import project, publish, STAGES

class CampaignPublisherTests(unittest.TestCase):
    def test_stage_linked_counts_and_private_fields(self):
        result = project({'campaign_id':'test','status':'running','mode':'stage_linked','current_stage':'1-2',
            'cleared_stages':['1-1','1-1','9-9'], 'restarts':2, 'api_key':'private',
            'artifacts':{'secret':'private'}, 'current':{'latency_ms':4.2,'djev_url':'private'},
            'stage_results':{'1-2':{'status':'running','attempts':3,'retries':2,'checkpoint_retries':1}},
            'event_log':[{'kind':'restart','message':'Retry from /home/alice/secret using https://private.test/key api_key=secret'}]})
        self.assertEqual(result['counts']['cleared'],1)
        self.assertEqual(result['counts']['restarts'],2)
        self.assertEqual(result['counts']['checkpoint_retries'],1)
        self.assertEqual(result['mode'],'stage_linked')
        self.assertNotIn('private.test',json.dumps(result))
        self.assertNotIn('secret',json.dumps(result))
        self.assertNotIn('api_key',result)
        self.assertNotIn('djev_url',result['current'])
    def test_missing_and_partial_status_preserve_last_good(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'source'; public=Path(folder)/'public'; source.mkdir()
            self.assertEqual(publish(source,public)['status'],'waiting_for_runner')
            (source/'status.json').write_text(json.dumps({'campaign_id':'one','mode':'continuous','status':'running'}))
            self.assertEqual(publish(source,public)['mode'],'continuous')
            (source/'status.json').write_text('{')
            result=publish(source,public)
            self.assertEqual(result['campaign_id'],'one')
            self.assertTrue(result['feed_error'])
    def test_frame_is_fixed_path_and_requires_jpeg(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'source'; public=Path(folder)/'public'; source.mkdir()
            (source/'status.json').write_text(json.dumps({'campaign_id':'one','artifacts':{'frame':'/etc/passwd'}}))
            (source/'latest-frame.jpg').write_bytes(b'not a jpeg')
            self.assertIsNone(publish(source,public)['frame'])
            (source/'latest-frame.jpg').write_bytes(b'\xff\xd8test')
            self.assertEqual(publish(source,public)['frame']['url'],'/data/campaign-frame.jpg')
    def test_final_links_require_complete_matching_verified_files(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'source'; public=Path(folder)/'public'; source.mkdir()
            dest=public/'campaign-final'/'campaign-one'; dest.mkdir(parents=True)
            raw={'campaign_id':'one','status':'completed','cleared_stages':STAGES,
                 'artifacts':{'replay_url':'/data/campaign-final/campaign-one/campaign-replay.mp4',
                              'verification_url':'/data/campaign-final/campaign-one/verification.json'}}
            def check():
                (source/'status.json').write_text(json.dumps(raw))
                return publish(source,public)['artifacts']
            self.assertEqual(check(),{})
            (dest/'campaign-replay.mp4').write_bytes(b'test-video')
            audit={'campaign_id':'one','completed':True,'replay_verified':False}
            (dest/'verification.json').write_text(json.dumps(audit))
            self.assertEqual(check(),{})
            audit['replay_verified']=True
            audit['replays']={'full':{'file':'campaign-replay.mp4','kind':'chronological_attempts','verified':True}}
            (dest/'verification.json').write_text(json.dumps(audit))
            self.assertEqual(check(),raw['artifacts'])
            raw['artifacts']['clears_url']='/data/campaign-final/campaign-one/campaign-clears.mp4'
            (dest/'campaign-clears.mp4').write_bytes(b'test-compilation')
            self.assertNotIn('clears_url',check())
            audit['replays']['clears']={'file':'campaign-clears.mp4','kind':'stitched_stage_clears','verified':True}
            (dest/'verification.json').write_text(json.dumps(audit))
            self.assertIn('clears_url',check())
            raw['artifacts']['audit_url']='/data/campaign-final/campaign-one/campaign-audit.tar.gz'
            (dest/'campaign-audit.tar.gz').write_bytes(b'test-archive')
            audit['audit_archive']={'file':'campaign-audit.tar.gz','verified':True}
            (dest/'verification.json').write_text(json.dumps(audit))
            self.assertIn('audit_url',check())
            raw['artifacts']['clears_url']='/data/campaign-final/other/campaign-clears.mp4'
            self.assertNotIn('clears_url',check())
            audit['replays']['full']['kind']='stitched_stage_clears'
            (dest/'verification.json').write_text(json.dumps(audit))
            self.assertEqual(check(),{})
            audit['replays']['full']['kind']='chronological_attempts'
            (dest/'verification.json').write_text(json.dumps(audit))
            raw['status']='running'; self.assertEqual(check(),{})
            raw['status']='completed'; raw['campaign_id']='other'; self.assertEqual(check(),{})
            raw['campaign_id']='one'; raw['cleared_stages']=STAGES[:-1]; self.assertEqual(check(),{})
            raw['cleared_stages']=STAGES
            raw['artifacts']['replay_url']='/data/campaign-final/../campaign-replay.mp4'
            self.assertEqual(check(),{})

    def test_nonfinite_and_unreported_timestamps(self):
        value=project({'current':{'latency_ms':float('nan')},'updated_at':'nope'})
        self.assertIsNone(value['current']['latency_ms'])
        self.assertIsNone(value['updated_at'])
        json.dumps(value,allow_nan=False)

if __name__=='__main__':unittest.main()
