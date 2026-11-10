"""One-night Codex resume supervisor; waits for quotas, never changes credentials.

Uses a fixed session UUID and local rollout to avoid resuming unrelated work.
No API calls during the wait. Logs/configuration live in ignored .tools/overnight.
"""
import argparse,datetime as dt,json,os,shutil,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UTC=dt.timezone.utc

def instant(value):
    if isinstance(value,(int,float)):return dt.datetime.fromtimestamp(value,UTC)
    return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(UTC)

def rollout_state(path):
    state='unknown';limits=None
    # Read only event metadata; never copy prompts, auth files or credentials.
    with Path(path).open(encoding='utf-8') as stream:
        for line in stream:
            try:r=json.loads(line)
            except json.JSONDecodeError:continue # Concurrent writer may have an incomplete final line.
            if r.get('type')!='event_msg':continue
            p=r.get('payload',{});event=p.get('type')
            if event in ('task_started','turn_started'):state='active'
            if event in ('task_complete','turn_complete','turn_aborted'):state='idle'
            if p.get('rate_limits'):limits=p['rate_limits']
            if event=='error' and any(s in json.dumps(p).lower() for s in ('usage_limit','rate_limit','usage limit','rate limit')):state='limited'
    return state,limits

def next_reset(limits,now):
    resets=[]
    for key in ('primary','secondary'):
        window=(limits or {}).get(key) or {}
        if window.get('used_percent',0)>=99 and window.get('resets_at'):
            resets.append(instant(window['resets_at'])+dt.timedelta(seconds=60))
    return max(resets) if resets else now+dt.timedelta(hours=5,minutes=1)

def command(cli,session,output,mode='fork'):
    # argv list + stdin: no shell interpolation, no secrets in the command line.
    return [cli,'exec','-C',str(ROOT),'-c','approval_policy="never"','-c','sandbox_mode="danger-full-access"',
            mode,session,'-','--json','-o',str(output)]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',required=True)
    parser.add_argument('--session-log',required=True,type=Path)
    parser.add_argument('--not-before',required=True,help='ISO8601 timestamp with timezone')
    parser.add_argument('--stop-at',required=True,help='Do not start another attempt after this timestamp')
    parser.add_argument('--max-attempts',type=int,default=2)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();uuid.UUID(args.session)
    assert args.session in args.session_log.name,'Rollout does not match fixed UUID'
    cli=shutil.which('codex');assert cli,'codex executable missing'
    wake=instant(args.not_before);deadline=instant(args.stop_at)
    assert wake<deadline and 1<=args.max_attempts<=4
    out=ROOT/'.tools/overnight';out.mkdir(parents=True,exist_ok=True)
    if args.dry_run:
        print(json.dumps(dict(wake=wake.isoformat(),deadline=deadline.isoformat(),state=rollout_state(args.session_log)[0],
            argv=command(cli,args.session,out/'last-message.txt'),attempts=args.max_attempts),indent=2));return
    import msvcrt
    lock=(out/'supervisor.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:raise SystemExit('Another supervisor owns this project lock')
    def log(event,**extra):
        record=dict(time=dt.datetime.now(UTC).isoformat(),event=event,**extra)
        with (out/'supervisor.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
        (out/'status.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    log('waiting',pid=os.getpid(),wake=wake.isoformat(),deadline=deadline.isoformat(),mode='fork')
    attempts=0
    while dt.datetime.now(UTC)<deadline:
        if (out/'STOP').exists():log('stopped_by_user');return
        now=dt.datetime.now(UTC)
        if now<wake:time.sleep(min(30,(wake-now).total_seconds()));continue
        state,limits=rollout_state(args.session_log)
        if state not in ('idle','limited'):
            log('waiting_for_current_turn',state=state);time.sleep(30);continue
        ready=out/'ready.json'
        if not ready.exists() or not json.loads(ready.read_text(encoding='utf-8')).get('ready'):
            log('waiting_for_handoff');time.sleep(30);continue
        attempts+=1
        stamp=dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
        logfile=out/f'exec-{stamp}-{attempts:02d}.jsonl'
        prompt=(ROOT/'docs/automation/continue_prompt.md').read_text(encoding='utf-8')
        log('starting',attempt=attempts,parent_session=args.session,mode='fork')
        with logfile.open('w',encoding='utf-8') as output:
            proc=subprocess.Popen(command(cli,args.session,out/'last-message.txt'),cwd=ROOT,stdin=subprocess.PIPE,
                stdout=output,stderr=subprocess.STDOUT,text=True,encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW)
            # One child at a time. A STOP file stops scheduling, not an in-flight write.
            proc.communicate(prompt);code=proc.returncode
        if code==0:log('completed',attempt=attempts);return
        content=logfile.read_text(encoding='utf-8',errors='replace').lower()
        writer_conflict='already has an active writer' in content
        limited=any(marker in content for marker in ('usage_limit_reached','rate_limit_exceeded','usage limit','rate limit'))
        log('attempt_failed',attempt=attempts,exit_code=code,quota_wait=limited,writer_conflict=writer_conflict,log=str(logfile))
        if writer_conflict:
            log('blocked_writer_conflict',message='No engineering work started. Inspect log; do not treat argument validation as a successful restart.')
            return
        if not limited or attempts>=args.max_attempts:return
        _,limits=rollout_state(args.session_log);wake=next_reset(limits,dt.datetime.now(UTC))
        log('quota_wait',wake=wake.isoformat())
    log('deadline_reached')

if __name__=='__main__':main()
