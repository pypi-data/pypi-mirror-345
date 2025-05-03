#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from Decay_feature import SingleCellFeatureExtractor

root = '/scr/data/skala_redox_data/241004_New_2DG+A549'
conditions = ['A549_Control-etc', 'A549_Cyanide']

extractor_nadh = SingleCellFeatureExtractor(root, conditions)
extractor_fad = SingleCellFeatureExtractor(root, conditions)

extractor_nadh.features_dict = extractor_nadh.extract_features("n")
extractor_fad.features_dict = extractor_fad.extract_features("f")

extractor_nadh.load_masks()
extractor_fad.masks_dict = extractor_nadh.masks_dict  # Use the same masks for FAD

print("Processing NADH...")
extractor_nadh.process_features()

print("Processing FAD...")
extractor_fad.process_features()

for key in extractor_nadh.features_dict:
    print(f"Processed NADH: {key}")
    feature_matrix = extractor_nadh.compute_matrix(extractor_nadh.features_dict[key], extractor_nadh.masks_dict.get(key, np.zeros((256,256))), 1)
    extractor_nadh.plot_features(feature_matrix, 25000)

for key in extractor_fad.features_dict:
    print(f"Processed FAD: {key}")
    feature_matrix = extractor_fad.compute_matrix(extractor_fad.features_dict[key], extractor_fad.masks_dict.get(key, np.zeros((256,256))), 0)
    extractor_fad.plot_features(feature_matrix, 6000)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




