#!/usr/bin/env python
# coding: utf-8

# In[1]:


from Decay_feature import SingleCellFeatureExtractor

extractor_nadh = SingleCellFeatureExtractor(path = "/home/MORGRIDGE/mogawa/mogawa/test.csv", image_type='n')
extractor_fad = SingleCellFeatureExtractor(path = "/home/MORGRIDGE/mogawa/mogawa/test.csv", image_type='f')

# from Decay_feature import SingleCellFeatureExtractor

# root = '/scr/data/skala_redox_data/241004_New_2DG+A549'
# conditions = ['A549_Control-etc', 'A549_Cyanide']

# extractor_nadh = SingleCellFeatureExtractor(root, conditions, image_type='n')
# extractor_fad = SingleCellFeatureExtractor(root, conditions, image_type='f')


# In[ ]:





# In[2]:


extractor_nadh.run()


# In[1]:


extractor_fad.run()


# In[ ]:





# In[ ]:




