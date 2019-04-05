import os

import ROOT

import PhysicsTools.HeppyCore.framework.config as cfg

from PhysicsTools.HeppyCore.framework.config import printComps
from PhysicsTools.HeppyCore.framework.heppy_loop import getHeppyOption

from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator
ComponentCreator.useLyonAAA = True

import logging
logging.shutdown()
# reload(logging)
logging.basicConfig(level=logging.WARNING)

from PhysicsTools.HeppyCore.framework.event import Event
Event.print_patterns = ['*taus*', '*muons*', '*electrons*', 'veto_*', 
                        '*dileptons_*', '*jets*']

###############
# Options
###############

# Get all heppy options; set via "-o production" or "-o production=True"

# production = True run on batch, production = False run locally
test = getHeppyOption('test', True)
syncntuple = getHeppyOption('syncntuple', False)
data = getHeppyOption('data', False)
embedded = getHeppyOption('embedded', True)
if embedded:
    data = True
add_sys = getHeppyOption('add_sys', True)
reapplyJEC = getHeppyOption('reapplyJEC', True)
# For specific studies
add_iso_info = getHeppyOption('add_iso_info', False)
add_tau_fr_info = getHeppyOption('add_tau_fr_info', False)

###############
# global tags
###############

from CMGTools.H2TauTau.heppy.sequence.common import gt_mc, gt_data, gt_embed

###############
# Components
###############

from CMGTools.RootTools.utils.splitFactor import splitFactor
from CMGTools.H2TauTau.proto.samples.component_index import ComponentIndex
import CMGTools.H2TauTau.proto.samples.fall17.higgs as higgs
index=ComponentIndex(higgs)

import CMGTools.H2TauTau.proto.samples.fall17.data as data_forindex
dindex = ComponentIndex(data_forindex)

from CMGTools.H2TauTau.proto.samples.fall17.higgs_susy import mssm_signals
from CMGTools.H2TauTau.proto.samples.fall17.higgs import sync_list
import CMGTools.H2TauTau.proto.samples.fall17.backgrounds as backgrounds_forindex
bindex = ComponentIndex( backgrounds_forindex)
backgrounds = backgrounds_forindex.backgrounds
import CMGTools.H2TauTau.proto.samples.fall17.embedded as embedded_forindex
eindex = ComponentIndex( embedded_forindex)
from CMGTools.H2TauTau.proto.samples.fall17.triggers_tauTau import mc_triggers, mc_triggerfilters
from CMGTools.H2TauTau.proto.samples.fall17.triggers_tauTau import data_triggers, data_triggerfilters, embedded_triggerfilters
from CMGTools.H2TauTau.heppy.sequence.common import puFileData, puFileMC

mc_list = backgrounds + sync_list + mssm_signals
data_list = data_forindex.data_tau
embedded_list = embedded_forindex.embedded_tt

n_events_per_job = 1e4
if embedded:
    n_events_per_job = 3e4

for sample in mc_list:
    sample.triggers = mc_triggers
    sample.triggerobjects = mc_triggerfilters
    sample.splitFactor = splitFactor(sample, n_events_per_job)
    sample.puFileData = puFileData
    sample.puFileMC = puFileMC
    sample.channel = 'tt'

for sample in data_list+embedded_list:
    sample.triggers = data_triggers
    sample.triggerobjects = data_triggerfilters
    sample.splitFactor = splitFactor(sample, n_events_per_job)
    era = sample.name[sample.name.find('2017')+4]
    if 'V32' in gt_data and era in ['D','E']:
        era = 'DE'
    sample.dataGT = gt_data.format(era)
    sample.channel = 'tt'

for sample in embedded_list:
    sample.triggerobjects = embed_triggerfilters
    sample.isEmbed = True

selectedComponents = mssm_signals#[x for x in backgrounds if x.name not in ['DY2JetsToLL_M50_LO','DY3JetsToLL_M50_LO','DYJetsToLL_M50','TTLep_pow','TTSemi_pow']]
if data:
    selectedComponents = data_list
    if embedded:
        selectedComponents = embedded_list


if test:
    cache = True
    # comp = bindex.glob('DYJetsToLL_M50_ext')[0]
    # comp = bindex.glob('WJetsToLNu_LO')[0]
    # comp = bindex.glob('TTLep_pow')[0]
    # comp = bindex.glob('TTHad_pow')[0]
    # comp = bindex.glob('TTSemi_pow')[0]
    comp = index.glob('HiggsVBF125')[0] 
    if data:
        comp = dindex.glob('Tau_Run2017B_31Mar2018')[0]
    if embedded:
        comp = eindex.glob('Embedded2017B_tt')[0]
    selectedComponents = [comp]
    # for comp in selectedComponents:
    #    comp.files = comp.files[:1]
    #    comp.splitFactor = 1
    #    comp.fineSplitFactor = 1
    #    comp.files = ['file1.root']

events_to_pick = []

#KIT's skimming function
def skim_KIT(event):
    flags = [
        'Flag_goodVertices',
        'Flag_globalTightHalo2016Filter',
        'Flag_globalSuperTightHalo2016Filter',
        'Flag_HBHENoiseFilter',
        'Flag_HBHENoiseIsoFilter',
        'Flag_EcalDeadCellTriggerPrimitiveFilter',
        'Flag_BadPFMuonFilter',
        'Flag_BadChargedCandidateFilter',
        'Flag_eeBadScFilter',
        'Flag_ecalBadCalibFilter']
    if embedded or data:
        flags = ['Flag_goodVertices','Flag_globalSuperTightHalo2016Filter','Flag_HBHENoiseFilter','Flag_HBHENoiseIsoFilter','Flag_EcalDeadCellTriggerPrimitiveFilter','Flag_BadPFMuonFilter','Flag_BadChargedCandidateFilter','Flag_eeBadScFilter','Flag_ecalBadCalibFilter']
    ids = [
        'againstElectronVLooseMVA6',
        'againstMuonLoose3',
        'byVLooseIsolationMVArun2017v2DBoldDMwLT2017']
    return all([getattr(event,x)==1 for x in flags]) and\
        event.veto_third_lepton_electrons_passed and\
        event.veto_third_lepton_muons_passed and\
        all([event.dileptons_sorted[0].leg2().tauID(x) for x in ids]) and\
        all([event.dileptons_sorted[0].leg1().tauID(x) for x in ids])


from CMGTools.H2TauTau.heppy.sequence.common import debugger
debugger.condition = None#skim_KIT#lambda event : True # lambda event : len(event.sel_taus)>2
###############
# Analyzers 
###############

from CMGTools.H2TauTau.heppy.analyzers.Selector import Selector
def select_tau(tau):
    return tau.pt()    > 40  and \
        abs(tau.eta()) < 2.1 and \
        abs(tau.leadChargedHadrCand().dz()) < 0.2 and \
        tau.tauID('decayModeFinding') > 0.5 and \
        abs(tau.charge()) == 1. and \
        tau.tauID('byVVLooseIsolationMVArun2017v2DBoldDMwLT2017')
sel_taus = cfg.Analyzer(
    Selector,
    'sel_taus',
    output = 'sel_taus',
    src = 'taus',
    filter_func = select_tau  
)

from CMGTools.H2TauTau.heppy.analyzers.EventFilter import EventFilter
two_tau = cfg.Analyzer(
    EventFilter, 
    'two_tau',
    src = 'sel_taus',
    filter_func = lambda x : len(x)>1
)

# ditau pair ================================================================

from CMGTools.H2TauTau.heppy.analyzers.DiLeptonAnalyzer import DiLeptonAnalyzer

dilepton = cfg.Analyzer(
    DiLeptonAnalyzer,
    output = 'dileptons',
    l1 = 'sel_taus',
    l2 = 'sel_taus',
    dr_min = 0.5
)

def sorting_metric(dilepton):
    leg1_iso = dilepton.leg1().tauID('byIsolationMVArun2017v2DBoldDMwLTraw2017')
    leg2_iso = dilepton.leg2().tauID('byIsolationMVArun2017v2DBoldDMwLTraw2017')
    if leg1_iso > leg2_iso:
        most_isolated_tau_isolation = leg1_iso
        most_isolated_tau_pt = dilepton.leg1().pt()
        least_isolated_tau_isolation = leg2_iso
        least_isolated_tau_pt = dilepton.leg2().pt()
    else:
        most_isolated_tau_isolation = leg2_iso
        most_isolated_tau_pt = dilepton.leg2().pt()
        least_isolated_tau_isolation = leg1_iso
        least_isolated_tau_pt = dilepton.leg1().pt()
    return (-most_isolated_tau_isolation,
             -most_isolated_tau_pt,
             -least_isolated_tau_isolation,
             -least_isolated_tau_pt)

from CMGTools.H2TauTau.heppy.analyzers.Sorter import Sorter
dilepton_sorted = cfg.Analyzer(
    Sorter,
    output = 'dileptons_sorted',
    src = 'dileptons',
    metric = sorting_metric,
    reverse = False
    )



sequence_dilepton = cfg.Sequence([
        sel_taus,
        two_tau,
        dilepton,
        dilepton_sorted,
        ])

# weights ================================================================

from CMGTools.H2TauTau.heppy.analyzers.TauIDWeighter import TauIDWeighter
tauidweighter = cfg.Analyzer(
    TauIDWeighter,
    'TauIDWeighter',
    taus = lambda event: [event.dileptons_sorted[0].leg1(),event.dileptons_sorted[0].leg2()]
)

# from CMGTools.H2TauTau.heppy.analyzers.FakeFactorAnalyzer import FakeFactorAnalyzer
# fakefactor = cfg.Analyzer(
#     FakeFactorAnalyzer,
#     'FakeFactorAnalyzer',
#     channel = 'tt',
#     filepath = '$CMSSW_BASE/src/HTTutilities/Jet2TauFakes/data/MSSM2016/20170628_medium/{}/{}/fakeFactors_20170628_medium.root',
#     met = 'pfmet'
# )

# ntuple ================================================================

if syncntuple:
    skim_func = lambda x: True
else:
    skim_func = lambda x: skim_KIT

from CMGTools.H2TauTau.heppy.analyzers.NtupleProducer import NtupleProducer
from CMGTools.H2TauTau.heppy.ntuple.ntuple_variables import tautau as event_content_tautau
ntuple = cfg.Analyzer(
    NtupleProducer,
    name = 'NtupleProducer',
    treename = 'events',
    event_content = event_content_tautau,
    skim_func = skim_func
)

# embedded ================================================================

from CMGTools.H2TauTau.heppy.analyzers.EmbeddedAnalyzer import EmbeddedAnalyzer
embedded_ana = cfg.Analyzer(
    EmbeddedAnalyzer,
    name = 'EmbeddedAnalyzer',
    channel = 'tt'
)


from CMGTools.H2TauTau.heppy.sequence.common import sequence_beforedil, sequence_afterdil, trigger, met_filters, trigger_match
sequence = sequence_beforedil
sequence.extend( sequence_dilepton )
sequence.extend( sequence_afterdil )
if embedded:
    sequence.append(embedded_ana)
# if data:
#     sequence.append(fakefactor)
sequence.append(tauidweighter)
sequence.append(ntuple)

if embedded:
    sequence = [x for x in sequence if x.name not in ['JSONAnalyzer']]

if events_to_pick:
    from CMGTools.H2TauTau.htt_ntuple_base_cff import eventSelector
    eventSelector.toSelect = events_to_pick
    sequence.insert(0, eventSelector)

# the following is declared in case this cfg is used in input to the
# heppy.py script
from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config(components=selectedComponents,
                    sequence=sequence,
                    services=[],
                    events_class=Events
                    )

printComps(config.components, True)

### systematics

nominal = config


from CMGTools.H2TauTau.heppy.analyzers.Calibrator import Calibrator

def config_TauEnergyScale(dm_name, gm_name, up_or_down):
    tau_energyscale_ana_index = nominal.sequence.index(tauenergyscale)
    new_config = copy.deepcopy(nominal)

    tau_calibrator = cfg.Analyzer(
        Calibrator,
        src = 'taus',
        calibrator_factor_func = lambda x: getattr(x,'TES_{}_{}_{}'.format(gm_name,dm_name,up_or_down),1.)
    )

    new_config.sequence.insert(tau_energyscale_ana_index+1, tau_calibrator)
    return new_config

def config_JetEnergyScale(group, up_or_down):
    jets_ana_index = nominal.sequence.index(jets)
    new_config = copy.deepcopy(nominal)

    jet_calibrator = cfg.Analyzer(
        Calibrator,
        src = 'jets',
        calibrator_factor_func = lambda x: getattr(x,"corr_{}_JEC_{}".format(group,up_or_down), 1./x.rawFactor()) * x.rawFactor()
    )

    new_config.sequence.insert(jets_ana_index+1, jet_calibrator)
    return new_config

# TODO harmonize energy scale among all susceptible objects
from CMGTools.H2TauTau.heppy.sequence.common import tauenergyscale, jets
import copy
configs = {'nominal':nominal}

### tau energy scale 
TES = [['HadronicTau','1prong0pi0'],
       ['HadronicTau','1prong1pi0'],
       ['HadronicTau','3prong0pi0'],
       ['HadronicTau','3prong1pi0'],
       ['promptMuon','1prong0pi0'],
       ['promptEle','1prong0pi0'],
       ['promptEle','1prong1pi0']]

for gm_name, dm_name in TES:
    configs['TES_{}_{}_up'.format(gm_name, dm_name)] = config_TauEnergyScale(dm_name, gm_name, 'up')
    configs['TES_{}_{}_down'.format(gm_name, dm_name)] = config_TauEnergyScale(dm_name, gm_name, 'down')

JES = ['CMS_scale_j_eta0to5_13Tev',
       'CMS_scale_j_eta0to3_13TeV',
       'CMS_scale_j_eta3to5_13TeV',
       'CMS_scale_j_RelativeBal_13TeV',
       'CMS_scale_j_RelativeSample_13TeV']

for source in JES:
    configs['{}_up'.format(source)] = config_JetEnergyScale(source,'up')
    configs['{}_down'.format(source)] = config_JetEnergyScale(source,'down')

print configs

config = configs['TES_{}_{}_up'.format('HadronicTau','1prong0pi0')]
