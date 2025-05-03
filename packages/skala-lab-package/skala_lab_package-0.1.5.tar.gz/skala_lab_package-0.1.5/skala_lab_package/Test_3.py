#!/usr/bin/env python
# coding: utf-8

# In[1]:


from Optimal_Transport import Optimal_Transport

root = '/scr/data/skala_redox_data/241004_New_2DG+A549'
conditions = ['A549_Control-etc', 'A549_Cyanide', 'A549_Control-gly', 'A549_2DG', 
              'A549_Sodium Arsenite', 'HeLa_Control-gly', 'HeLa_2DG', 'HeLa_Sodium Arsenite']

ot_analyzer = Optimal_Transport(root, conditions)

ot_analyzer.load_decay_data()

ot_analyzer.compute_global_pca(n_components=10)

pairs = [
    ('HeLa_Control-gly', 'HeLa_2DG'),
    ('HeLa_Control-gly', 'HeLa_Sodium Arsenite')
]

ot_analyzer.plot_ot_distances(pairs)

result = ot_analyzer.get_ot_distance('HeLa_Control-gly', 'HeLa_2DG')
if result:
    M1, M = result["M1"], result["M"]

    ot_analyzer.compare_distance_histograms(M1, M)
    ot_analyzer.compare_distance_histograms_fair(M1, M)


# In[ ]:




