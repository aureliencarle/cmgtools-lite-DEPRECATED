import copy

from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator

creator = ComponentCreator()
dbsInstance='phys03'

json='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'

#kreator.makeDataComponent("JetHT_Run2016B_PromptReco_v2"         , "/JetHT/Run2016B-PromptReco-v2/MINIAOD"         , "CMS",      ".*root", json)

data_single_muon_B_to_G = creator.makeDataComponent(
    "data_single_muon", 
   "/SingleMuon/cbernet-MINIAOD_CL_2-3ac6ceef15bb149c4b22dc59e3cfeade/USER", # not the right one ?
    "CMS", ".*root", json)

data_single_muon = [data_single_muon_B_to_G]


data_single_electron = [] #[SingleElectron_Run2016B_23Sep2016, SingleElectron_Run2016C_23Sep2016, SingleElectron_Run2016D_23Sep2016, SingleElectron_Run2016E_23Sep2016, SingleElectron_Run2016F_23Sep2016, SingleElectron_Run2016G_23Sep2016]


data_muon_electron = [] #[MuonEG_Run2016B_23Sep2016, MuonEG_Run2016C_23Sep2016, MuonEG_Run2016D_23Sep2016, MuonEG_Run2016E_23Sep2016, MuonEG_Run2016F_23Sep2016, MuonEG_Run2016G_23Sep2016]


data_tau = [] #[Tau_Run2016B_03Feb2017_v2, Tau_Run2016C_03Feb2017, Tau_Run2016D_03Feb2017, Tau_Run2016E_03Feb2017, Tau_Run2016F_03Feb2017, Tau_Run2016G_03Feb2017, Tau_Run2016H_03Feb2017_v2, Tau_Run2016H_03Feb2017_v3]