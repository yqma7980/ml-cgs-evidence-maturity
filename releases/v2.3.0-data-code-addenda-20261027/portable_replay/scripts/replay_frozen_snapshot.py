"""Opt-in replay of a privacy-projected frozen snapshot. Not executed during preparation."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import itertools
import json

R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def write(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or list(dict.fromkeys(k for x in rows for k in x))
    with p.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dump(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def replay(folder, out=None, reference=None):
    # Only the frozen unit table, rule object and unchanged historical chain supply scientific inputs.
    units=read(folder/'FINAL_SCIENCE_SNAPSHOT.csv');idx={x['paper_id']:x for x in units}
    rules=json.loads((folder/'DERIVATION_RULES_FROZEN.json').read_text(encoding='utf8'))
    binding=json.loads((folder/'PORTABLE_BINDINGS.json').read_text(encoding='utf8'))
    assert binding['source_history_sha256']==rules['frozen_history_sha256']
    assert sha(folder/'HISTORICAL627_FROZEN.csv')==binding['curated_history_sha256']
    rules['frozen_history_sha256']=binding['curated_history_sha256']
    version=rules['science_version'];scores=rules['scores'];metrics=rules['metrics'];diagnostics=rules['diagnostics']
    out=out or R/'replay_output';out.mkdir(parents=True,exist_ok=True)
    states=['POSITIVE','NON_POSITIVE','NR','U','NA','REVIEW_PENDING','UNKNOWN']
    def project(f,v):
        if v in rules['missing']:return rules['missing'][v]
        if v in rules['typed_contract'][f]['positive']:return 'POSITIVE'
        if v in rules['typed_contract'][f]['non_positive']:return 'NON_POSITIVE'
        raise ValueError(f'Unmapped typed input: {f}={v!r}')
    def union(ss):
        for state in ['POSITIVE','UNKNOWN','U','NR']:
            if state in ss:return state
        return 'NA'if all(s=='NA'for s in ss)else 'NON_POSITIVE'
    scopes={name:[x['paper_id']for x in units if x[field]=='true']for name,field in
            [('working_main','current_working_member'),('verified_journal','current_verified_journal_member')]}
    assert set(scopes['verified_journal'])<=set(scopes['working_main'])
    liu=json.loads((folder/'LIU_GHGT_UNIT_AUTHORITY.json').read_text(encoding='utf8'))
    assert liu['analysis_unit_id']in scopes['working_main'] and liu['analysis_unit_id']not in scopes['verified_journal']
    assert liu['inventory_paper_id']not in scopes['working_main']
    assert idx['ESR_RefNone_173']['geochemistry_diagnostic']=='diagnostic_checked'
    assert idx['ESR_RefNone_173']['physical_consistency_score']=='3'
    assert idx['ESR_RefNone_173']['physical_consistency_score_state']=='scored'
    outcomes=[];components=[];score_rows=[];maps=[]
    for scope,ids in scopes.items():
        for pid in ids:
            x=idx[pid]
            for f,metric in metrics.items():
                outcomes.append(dict(scope=scope,paper_id=pid,metric=metric,field=f,raw_value=x[f],status=project(f,x[f]),data_version=version))
            ss=[]
            for f in diagnostics:
                state=project(f,x[f]);ss.append(state)
                components.append(dict(scope=scope,paper_id=pid,field=f,raw_value=x[f],status=state,data_version=version))
            outcomes.append(dict(scope=scope,paper_id=pid,metric='physical_diagnostic_union7',field='DERIVED_SEVEN_COMPONENT_UNION',
                                 raw_value=';'.join(x[f]for f in diagnostics),status=union(ss),data_version=version))
            for f in scores:
                state,value=x[f+'_state'],x[f]
                assert state in rules['permitted_score_states']
                assert (state=='scored'and value in {'0','1','2','3','4'})or(state!='scored'and value=='')
                score_rows.append(dict(scope=scope,paper_id=pid,dimension=f,raw_score=value,raw_state=state,
                                       analysis_state=state,analysis_score=value if state=='scored'else'',data_version=version))
            maps.append(dict(scope=scope,paper_id=pid,**{f:rules['identifier_aliases'].get(x['mapping_'+f],x['mapping_'+f])for f in rules['map_fields']},data_version=version))
    summary=[]
    for scope,ids in scopes.items():
        for metric in list(metrics.values())+['physical_diagnostic_union7']:
            counts=Counter(x['status']for x in outcomes if x['scope']==scope and x['metric']==metric)
            assert sum(counts.values())==len(ids) and not counts['REVIEW_PENDING']and not counts['UNKNOWN']
            summary.append(dict(scope=scope,metric=metric,N=len(ids),**{s:counts[s]for s in states},
                                Available=counts['POSITIVE']+counts['NON_POSITIVE'],data_version=version))
    distributions=[];pairs=[]
    sx={(x['scope'],x['paper_id'],x['dimension']):x for x in score_rows}
    for scope,ids in scopes.items():
        for dim in scores:
            cc=Counter(x['analysis_score']if x['analysis_state']=='scored'else x['analysis_state']for x in score_rows if x['scope']==scope and x['dimension']==dim)
            distributions.append(dict(scope=scope,dimension=dim,N=len(ids),**{'score_'+str(i):cc[str(i)]for i in range(5)},
                                      **{s:cc[s]for s in ['not_reported','unclear','not_applicable','unknown','REVIEW_PENDING']},
                                      scored_N=sum(cc[str(i)]for i in range(5)),data_version=version))
        for a,b in itertools.combinations(scores,2):
            cc=Counter();missing=Counter()
            for pid in ids:
                x,y=sx[(scope,pid,a)],sx[(scope,pid,b)]
                if x['analysis_state']==y['analysis_state']=='scored':cc[(int(x['analysis_score']),int(y['analysis_score']))]+=1
                else:missing[(x['analysis_state'],y['analysis_state'])]+=1
            n=sum(cc.values())
            rows=[dict(scope=scope,dimension_A=a,dimension_B=b,score_A=i,score_B=j,count=cc[(i,j)],pair_effective_N=n,total_N=len(ids),data_version=version)for i,j in itertools.product(range(5),repeat=2)]
            pairs+=rows
            write(out/f'COOCCURRENCE_{scope}_{a}__{b}.csv',rows)
            write(out/f'MISSING_MARGINS_{scope}_{a}__{b}.csv',[dict(state_A=a,state_B=b,count=n)for(a,b),n in sorted(missing.items())],['state_A','state_B','count'])
    history=read(folder/'HISTORICAL627_FROZEN.csv');assert len(history)==627
    hist_ids={x['paper_id']for x in history};assert len(hist_ids)==57
    def hp(f,v):
        if f in metrics:return project(f,v)if v else'NO_LOCKED_VALUE'
        return 'SCORE_'+v if v in {'0','1','2','3','4'}else'HISTORICAL_UNSCORED_OR_NO_VALUE'
    chains=[]
    for h in history:
        pid,f=h['paper_id'],h['field'];now=idx[pid][f];op,np=hp(f,h['final_value']),hp(f,now)
        pending=set(idx[pid]['historical_scope_excluded_pending_fields'].split(';'))
        if f in scores and (f in pending or f+'_state'in pending):np='REVIEW_PENDING'
        flags=[]
        if h['final_value']!=now:
            if op==np:flags.append('CATEGORY_CHANGE_SAME_INDICATOR')
            elif f in scores:flags.append('SCORE_CHANGE')
            elif np=='POSITIVE':flags.append('POSITIVE_ENTRY')
            elif op=='POSITIVE':flags.append('POSITIVE_EXIT')
            else:flags.append('MISSING_OR_NONPOSITIVE_STATE_CHANGE')
        if np=='REVIEW_PENDING':flags=(flags or['NO_VALUE_CHANGE'])+['AUTHOR_DEFERRED_CURRENT_ANALYSIS']
        chains.append(dict(h,data_version=version,current_final_value=now,final_analysis_projection=np,
                           final_change_axis=';'.join(flags or['NO_VALUE_CHANGE']),current_working_member=str(pid in scopes['working_main']).lower(),
                           current_verified_journal_member=str(pid in scopes['verified_journal']).lower()))
    layers=[];origins=[]
    for f,metric in metrics.items():
        hs=[x for x in chains if x['field']==f]
        for layer,key in [('initial','locked_value'),('manual_recoding','reviewer_value'),('adjudicated','final_value'),('current','current_final_value')]:
            cc=Counter(hp(f,x[key])for x in hs)
            layers.append(dict(metric=metric,layer=layer,historical_records_N=57,positive=cc['POSITIVE'],non_positive=cc['NON_POSITIVE'],
                               NR=cc['NR'],U=cc['U'],NA=cc['NA'],no_locked_value=cc['NO_LOCKED_VALUE'],Available=cc['POSITIVE']+cc['NON_POSITIVE'],data_version=version))
        cc=Counter(x['history_origin_axis']for x in hs if x['final_analysis_projection']=='POSITIVE'and x['paper_id']in scopes['working_main'])
        origins.extend(dict(metric=metric,history_origin=k,count=n,data_version=version)for k,n in cc.items())
    coverage=[dict(paper_id=pid,historical57_manual_coverage='yes'if pid in hist_ids else'no',data_version=version)for pid in scopes['working_main']]
    output={
        'SEVEN_INDICATORS_ALL_MEMBERS_FINAL.csv':outcomes,'SEVEN_INDICATORS_SUMMARY_FINAL.csv':summary,
        'PHYSICAL_SEVEN_COMPONENTS_FINAL.csv':components,'FIVE_SCORES_ALL_MEMBERS_FINAL.csv':score_rows,
        'FIVE_SCORE_DISTRIBUTIONS_FINAL.csv':distributions,'TEN_PAIRS_ALL_JOINT_COUNTS_FINAL.csv':pairs,
        'DECISION_METHOD_ALL_MEMBERS_FINAL.csv':maps,'TableS16f_HISTORY627_CURRENT_CHAIN_FINAL.csv':chains,
        'TableS16g_POSITIVE_ENTRIES_EXITS_FINAL.csv':[x for x in chains if 'POSITIVE_ENTRY'in x['final_change_axis']or'POSITIVE_EXIT'in x['final_change_axis']],
        'TableS16h_HISTORICAL57_LAYER_COUNTS_FINAL.csv':layers,'TableS16i_CURRENT_POSITIVE_HISTORY_ORIGINS_FINAL.csv':origins,
        'HISTORICAL_MANUAL_COVERAGE_FINAL.csv':coverage}
    membership=[{k[len('membership_'):]:v for k,v in x.items()if k.startswith('membership_')}for x in units]
    for x in membership:assert x['paper_id']in idx
    output['TableS09_current_source_member_view_FINAL.csv']=membership
    output['TableS09_FINAL.csv']=membership
    output['TableS09a_FINAL.csv']=[x for x in membership if x['main_decision']==x['strict_journal_decision']=='INCLUDE']
    output['PHYSICAL_SCORE_UNION_CONCORDANCE_FINAL.csv']=[dict(scope=scope,paper_id=pid,
        physical_score=sx[scope,pid,'physical_consistency_score']['analysis_score'],
        score_state=sx[scope,pid,'physical_consistency_score']['analysis_state'],
        union_state=next(x['status']for x in outcomes if x['scope']==scope and x['paper_id']==pid and x['metric']=='physical_diagnostic_union7'),
        score_3_or_4=sx[scope,pid,'physical_consistency_score']['analysis_score']in {'3','4'},data_version=version)
        for scope,ids in scopes.items()for pid in ids]
    groups=[dict(analysis_unit_id=pid,raw_application_group=idx[pid]['application_group'],
        display_group='Cross-cutting / unmapped (display only)'if idx[pid]['application_group']in {'Unmapped applications','Cross-cutting and other'}else idx[pid]['application_group'],
        assignment_kind='DISPLAY_COMPRESSION_ONLY_NO_SCIENTIFIC_RECLASSIFICATION',data_version=version)for pid in scopes['working_main']]
    output['SIX_DISPLAY_GROUP_CROSSWALK_FINAL.csv']=groups
    group_index={x['analysis_unit_id']:x['display_group']for x in groups};group_states=[]
    for group in dict.fromkeys(group_index.values()):
        n=sum(v==group for v in group_index.values())
        for metric in list(metrics.values())+['physical_diagnostic_union7']:
            cc=Counter(x['status']for x in outcomes if x['scope']=='working_main'and x['metric']==metric and group_index[x['paper_id']]==group)
            assert sum(cc.values())==n
            group_states.append(dict(display_group=group,metric=metric,N=n,positive=cc['POSITIVE'],non_positive=cc['NON_POSITIVE'],
                NR=cc['NR'],U=cc['U'],NA=cc['NA'],available=cc['POSITIVE']+cc['NON_POSITIVE']))
    output['SIX_DISPLAY_GROUP_INDICATORS_FINAL.csv']=group_states
    for name,rows in output.items():write(out/name,rows)
    # Comparison is a read-only verification target, never an input to classification or counting.
    checks=[]
    for name,rows in output.items():
        if reference is None:continue
        target=reference/name
        if not target.exists():raise FileNotFoundError(target)
        produced=read(out/name);reference_rows=read(target)
        fields=list(produced[0]);p=Counter(tuple(x[k]for k in fields)for x in produced)
        q=Counter(tuple(x[k]for k in fields)for x in reference_rows)
        assert p==q,name
        checks.append(dict(object=name,rows=len(produced),recomputed_from_frozen_snapshot=True,match_existing_candidate=True))
    if checks:write(out/'CURRENT_CANDIDATE_PARITY.csv',checks)
    scope_info={s:len(ids)for s,ids in scopes.items()}
    result=dict(science_version=version,snapshot_schema='SINGLE_ENTRY_UNITS_MEMBERSHIP_MAPPING_V2',
                frozen_snapshot_sha256=sha(folder/'FINAL_SCIENCE_SNAPSHOT.csv'),scopes=scope_info,
                seven_primary_positive=[x['POSITIVE']for x in summary if x['scope']=='working_main'],
                seven_primary_available=[x['Available']for x in summary if x['scope']=='working_main'],
                physical_score_3_or_4=sum(x['analysis_score']in {'3','4'}for x in score_rows if x['scope']=='working_main'and x['dimension']=='physical_consistency_score'),
                history627_curated_projection_hash_unchanged=sha(folder/'HISTORICAL627_FROZEN.csv')==rules['frozen_history_sha256'],
                current_history_overlap=sum(x['historical57_manual_coverage']=='yes'for x in coverage),
                current_outside_history=sum(x['historical57_manual_coverage']=='no'for x in coverage),
                all_replayed_views_match=True if reference is not None else 'NOT_COMPARED_IN_PORTABLE_REPLAY',scientific_decisions_reapplied=0,CORE_writeback=False,
                remaining_primary_science_gates=0,scientific_freeze=True,checks=checks)
    dump(out/'SINGLE_SNAPSHOT_REPLAY_QA.json',result)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-only',action='store_true',required=True)
    parser.add_argument('--snapshot',type=Path,default=R/'FINAL_SCIENCE_SNAPSHOT')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    folder=args.snapshot.resolve();out=args.output.resolve()
    if out.is_relative_to(R.resolve()) or out==folder or folder.is_relative_to(out):
        parser.error('Use a separate output directory outside this archive content')
    print(json.dumps(replay(folder,out,reference=None),ensure_ascii=False))
