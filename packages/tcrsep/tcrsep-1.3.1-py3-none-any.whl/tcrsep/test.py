# # # from collections import defaultdict
# # # import pandas as pd 
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # import os
# # # import pickle
# # # from scipy.stats import ttest_ind as ttest
# # # import os
# # # import sys
# # # import inspect
# # # import logging
# # # from tqdm import tqdm
# # # from tcrsep.sharing_analysis import DATCR,Sharing
# # # from tcrsep.estimator import load_tcrsep,TCRsep
# # # from scipy.stats import pearsonr as PR

# #total 103105 parameters

# # #done
# # # sharing_predictor = Sharing('data/sharing')
# # # sharing_pre,sharing_real = sharing_predictor.predict_sharing('results/test/query_data.csv',get_actual_sharing=True)
# # # spectrum_pre,spectrum_real = sharing_predictor.sharing_spectrum(gen_model_path='models/generation_model/human_T_beta',sel_model_path='results/test2/tcrsep.pth' ,est_num=100000) 

# # # DATCR_predictor = DATCR('data/sharing')
# # # pvalues = DATCR_predictor.pvalue('results/test/query_data.csv')

# # from tcrsep.estimator import TCRsep
# # # sel_model = TCRsep(default_sel_model=True)
# # # sel_model = load_tcrsep('models/selection_model/COVID')
# # # sel_model = load_tcrsep('models/selection_model/CMV')
# # # sel_model = TCRsep(default_sel_model=True)
# # # sel_model = load_tcrsep()
# # # sel_model = TCRsep()
# # # post_seqs = np.array(pd.read_csv('data/demo/post_seqs.csv')[['CDR3.beta','V','J']])
# # # pre_seqs = np.array(pd.read_csv('data/demo/gen_seqs.csv')[['CDR3.beta','V','J']])
# # # sel_model.train(20,post_seqs,pre_seqs,valid_ratio=0.0)
# # # ws,emb = sel_model.predict_weights(post_seqs,return_emb=True)
# # # print(emb.shape)
# # # import gzip
# # # f = gzip.GzipFile('data/demo/post_embedding.npy.gz', "w") 
# # # np.save(file=f, arr=emb)
# # # ws,emb = sel_model.predict_weights(pre_seqs,return_emb=True)
# # # print(emb.shape)
# # # import gzip
# # # f = gzip.GzipFile('data/demo/gen_embedding.npy.gz', "w") 
# # # np.save(file=f, arr=emb)
# # # exit()

# # from tcrsep.estimator import TCRsep
# # sel_model = TCRsep(default_sel_model=True)
# # query_tcrs = [['CASSLGAGGSGTEAFF','TRBV7-9','TRBJ1-1'], ['CASTKAGGSSYEQYF','TRBV6-5','TRBJ2-7']]
# # sel_factors = sel_model.predict_weights(query_tcrs) #obtain selection factors
# # pgens, pposts = sel_model.get_prob(query_tcrs) #obtain pre- and post-selection probs 

# # # draw samples from p_post
# # post_samples = sel_model.sample(N=1000)

# # from tcrsep.sharing_analysis import Sharing, DATCR
# # sharing_predictor = Sharing('data/sharing') 

# # # predict sharing numbers of TCRs in query_data.csv among reps in the folder, "data/sharing"
# # sharing_pre,sharing_real = sharing_predictor.predict_sharing('data/query_data_evaled.csv') 

# # # predict the sharing spectrum for reps in "data/sharing"
# # spectrum_pre,spectrum_real = sharing_predictor.sharing_spectrum(est_num=10000) 

# # # identify DATCRs
# # DATCR_predictor = DATCR('data/sharing')
# # pvalues = DATCR_predictor.pvalue('data/query_data_evaled.csv')

# # import pandas as pd
# # from tcrsep.estimator import TCRsep
# # #Load data
# # post_df = pd.read_csv('data/demo/post_seqs.csv')
# # gen_df = pd.read_csv('data/demo/gen_seqs.csv')
# # post_samples = post_df[['CDR3.beta','V','J']].values
# # gen_samples = gen_df[['CDR3.beta','V','J']].values

# # #Infer the selection model
# # sel_model = TCRsep()
# # sel_model.train(50,post_samples,gen_samples,valid_ratio=0.0)

# # #Load sequence data and predict selection factors
# # predictions = sel_model.predict_weights(post_samples)

# # #Save the TCRsep model
# # sel_model.save(save_dir='results/testNN')

# # #Load the TCRsep model
# # from tcrsep.estimator import load_tcrsep
# # sel_model = load_tcrsep(load_dir='results/testNN')
# # exit()

# import gzip
# import pandas as pd
# from tcrsep.estimator import TCRsep,load_tcrsep
# import pandas as pd

# #test real data HIP01597_HIP17577 ~18.2
# #HIP13185_HIP10389
# # post_df = pd.read_csv('data/test/post_train.csv')
# # gen_df = pd.read_csv('data/test/pre_train.csv')
# # post_samples = post_df[['CDR3.beta','V','J']].values
# # gen_samples = gen_df[['CDR3.beta','V','J']].values

# sel_model = TCRsep()
# model = sel_model.model
# print(sum(p.numel() for p in model.parameters() if p.requires_grad))
# exit()
# sel_model.train(500,post_samples,gen_samples)
# sel_model.save('results/testn')

# post_df = pd.read_csv('data/test/post_test.csv')
# gen_df = pd.read_csv('data/test/pre_test.csv')
# post_df = post_df.loc[(post_df['sel_new']<100) &(post_df['sel_new'] > 0.01)]
# gen_df = gen_df.loc[(gen_df['sel_new']<100) &(gen_df['sel_new'] > 0.01)]
# post_samples2 = post_df[['CDR3.beta','V','J']].values
# gen_samples2 = gen_df[['CDR3.beta','V','J']].values
# sel_post,sel_pre = sel_model.predict_weights(post_samples2),sel_model.predict_weights(gen_samples2)
# sels1 = post_df['sel_new'].values
# sels2 = gen_df['sel_new'].values
# import numpy as np
# sels_pre = np.array(list(sel_post) + list(sel_pre))
# sels_true = np.array(list(sels1) + list(sels2))
# rr = np.abs(sels_true - sels_pre) / sels_true * 100
# from scipy.stats import pearsonr as PR
# PR(np.log(sels_pre),np.log(sels_true))
# exit()

# #loading data
# post_df = pd.read_csv('data/demo/post_seqs.csv')
# gen_df = pd.read_csv('data/demo/gen_seqs.csv')
# post_samples = post_df[['CDR3.beta','V','J']].values
# gen_samples = gen_df[['CDR3.beta','V','J']].values

# #infer the selection model
# sel_model = TCRsep()
# sel_model.train(50,post_samples,gen_samples,valid_ratio=0.0)

# #Load sequence data and predict selection factors
# predictions = sel_model.predict_weights(post_samples)
# print(predictions[:5])

# sel_model.save('results/testN')

# sel_model = load_tcrsep('results/testN')
# print(sel_model.predict_weights(post_samples)[:5])
# exit()
# #sel_tcrsep_Z_oriemb_a0.1_d0.0_b512_reg3 is the tcrsep column

# sel_model = load_tcrsep('results/test0/')
# query_tcrs = [['CASSLGAGGSGTEAFF','TRBV7-9','TRBJ1-1'], ['CASTKAGGSSYEQYF','TRBV6-5','TRBJ2-7']]
# sel_factors = sel_model.predict_weights(query_tcrs) #obtain selection factors
# print(sel_factors[:5])
# sel_factors_ = sel_model.predict_weights(np.random.randn(2,256)) #obtain selection factors
# print(sel_factors_[:5])
# pgens, pposts = sel_model.get_prob(query_tcrs) #obtain pre- and post-selection probs 
# print(pgens[:5],pposts[:5])
# print(PR(np.log(sel_pre),np.log(sel_true)))
# # draw samples from p_post
# post_samples = sel_model.sample(N=10)
# print(post_samples)
# exit()

# from tcrsep.sharing_analysis import Sharing, DATCR
# sharing_predictor = Sharing('data/sharing')

# # predict sharing numbers of TCRs in query_data.csv among reps in the folder, "data/sharing"
# sharing_pre,sharing_real = sharing_predictor.predict_sharing('data/query_data_evaled.csv') 
# print(sharing_pre[:5])
# print(sharing_real[:5])

# # predict the sharing spectrum for reps in "data/sharing"
# spectrum_pre,spectrum_real = sharing_predictor.sharing_spectrum(sel_model_path='results/test0', est_num=10000) 
# print(spectrum_pre)
# print(spectrum_real)

# # identify DATCRs
# DATCR_predictor = DATCR('data/sharing')
# pvalues = DATCR_predictor.pvalue('data/query_data_evaled.csv')
# print(pvalues[:5])

from tcrsep.estimator import TCRsep
sel_model = TCRsep(default_sel_model=True)
query_tcrs = [['CASSLGAGGSGTEAFF','TRBV7-9','TRBJ1-1'], ['CASTKAGGSSYEQYF','TRBV6-5','TRBJ2-7']]
sel_factors = sel_model.predict_weights(query_tcrs) #obtain selection factors
pgens, pposts = sel_model.get_prob(query_tcrs) #obtain pre- and post-selection probs 

# draw samples from p_post
post_samples = sel_model.sample(N=10)
from tcrsep.sharing_analysis import Sharing, DATCR
sharing_predictor = Sharing('data/sharing') 

# predict sharing numbers of TCRs in query_data.csv among reps in the folder, "data/sharing"
sharing_pre,sharing_real = sharing_predictor.predict_sharing('data/query_data_evaled.csv') 

# predict the sharing spectrum for reps in "data/sharing"
spectrum_pre,spectrum_real = sharing_predictor.sharing_spectrum(est_num=1000) 

# identify DATCRs
DATCR_predictor = DATCR('data/sharing')
pvalues = DATCR_predictor.pvalue('data/query_data_evaled.csv')

import pandas as pd
from tcrsep.estimator import TCRsep
#Load data
post_df = pd.read_csv('data/demo/post_seqs.csv')
gen_df = pd.read_csv('data/demo/gen_seqs.csv')
post_samples = post_df[['CDR3.beta','V','J']].values
gen_samples = gen_df[['CDR3.beta','V','J']].values

#Infer the selection model
sel_model = TCRsep()
sel_model.train(50,post_samples,gen_samples,valid_ratio=0.0)

#Load sequence data and predict selection factors
predictions = sel_model.predict_weights(post_samples)

#Save the TCRsep model
sel_model.save(save_dir='test')

#Load the TCRsep model
from tcrsep.estimator import load_tcrsep
sel_model = load_tcrsep(load_dir='test')