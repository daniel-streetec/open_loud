import datetime as dt,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from resume_after_reset import next_reset,command,instant
class SupervisorChecks(unittest.TestCase):
    def test_wait_for_later_exhausted_window(self):
        now=instant('2026-11-09T22:00:00Z')
        limits={'primary':{'used_percent':100,'resets_at':now.timestamp()+100},'secondary':{'used_percent':100,'resets_at':now.timestamp()+200}}
        self.assertEqual(next_reset(limits,now),now+dt.timedelta(seconds=260))
    def test_fixed_uuid_and_stdin_no_shell(self):
        args=command('C:/Program Files/Codex/codex.exe','fixed-session',Path('result.txt'))
        self.assertIn('resume',args);self.assertIn('fixed-session',args);self.assertNotIn('--last',args)
        self.assertEqual(args[args.index('fixed-session')+1],'-')
