from __future__ import absolute_import

import os
import numpy
import pandas as pd
import neurovault
import pylab as plt
import nibabel as nib
from celery import shared_task
from scipy.stats.stats import pearsonr
from nilearn.plotting import plot_glass_brain
from nilearn.image import resample_img
from django.shortcuts import get_object_or_404
from neurovault.apps.statmaps.models import Image, Similarity, Comparison


@shared_task
def generate_glassbrain_image(nifti_file,pk):
  nifti_file = str(nifti_file)
  png_img_name = "glass_brain_%s.png" % pk
  png_img_path = os.path.join(os.path.split(nifti_file)[0],png_img_name)
  glass_brain = plot_glass_brain(nifti_file)
  glass_brain.savefig(png_img_path)
  plt.close('all')


@shared_task
def save_voxelwise_pearson_similarity(pk1,pk2,resample_dim=[4,4,4]):

  # We will always calculate Comparison 1 vs 2, never 2 vs 1
  if pk1!=pk2:
    sorted_images = get_images_by_ordered_id(pk1,pk2)
    image1 = sorted_images[0]; image2 = sorted_images[1]
    pearson_metric = Similarity.objects.filter(similarity_metric="pearson product-moment correlation coefficient",transformation="voxelwise")[0]

    if not Comparison.objects.filter(image1=image1,image2=image2,similarity_metric=pearson_metric).exists():
      pearson_score = calculate_voxelwise_pearson_similarity(image1,image2,resample_dim)

      # create new Comparison with the voxelwise pearson similarity metric
      pearson_comparison = Comparison(image1=image1,
                                  image2=image2,
                                  similarity_metric=pearson_metric,
                                  similarity_score=pearson_score)
      pearson_comparison.save()


@shared_task
def update_voxelwise_pearson_similarity(pk1,pk2,resample_dim=[4,4,4]):

  if pk1!=pk2:
    sorted_images = get_images_by_ordered_id(pk1,pk2)
    image1 = sorted_images[0]; image2 = sorted_images[1]
    pearson_metric = Similarity.objects.filter(similarity_metric="pearson product-moment correlation coefficient",transformation="voxelwise")[0]
    if Comparison.objects.filter(image1=image1,image2=image2,similarity_metric=pearson_metric).exists():
      pearson_score = calculate_voxelwise_pearson_similarity(image1,image2,resample_dim)
      pearson_comparison = Comparison.objects.filter(image1=image1,image2=image2,similarity_metric=pearson_metric).update(similarity_score=pearson_score)

# Helper functions
'''Return list of Images sorted by the primary key'''
def get_images_by_ordered_id(pk1,pk2):
  image1 = get_object_or_404(Image, pk=pk1)
  image2 = get_object_or_404(Image, pk=pk2)
 
  # Sort images by the key (I'm sure there is a better way to do this)
  images = dict()
  images[image1.pk] = image1
  images[image2.pk] = image2
  inputs = [] 
  for pks,image in images.iteritems():
    inputs.append(image)
  
  # Now image 1 and 2 are ordered by the primary keys
  return inputs

'''Calculate a voxelwise pearson correlation via pairwise deletion'''
def calculate_voxelwise_pearson_similarity(image1,image2,resample_dim):

    # Get standard space brain
    reference = os.path.join(os.environ['FREESURFER_HOME'],'subjects', 'fsaverage', 'mri', 'brain.nii.gz')
    image_paths = [image.file.path for image in [image1,image2]]
    images_resamp, reference_resamp = resample_multi_images_ref(image_paths,reference,resample_dim)

    # Calculate correlation only on voxels that are in both maps (not zero, and not nan)
    binary_mask = make_binary_deletion_mask(images_resamp)
    image1 = images_resamp[0]; image2 = images_resamp[1]

    # Calculate correlation with voxels within mask
    return pearsonr(image1.get_data()[binary_mask==1],image2.get_data()[binary_mask==1])[0]


'''Make a nonzero, non-nan mask for a or or more images (registered, equally sized)'''
def make_binary_deletion_mask(images):

    if isinstance(images,nib.nifti1.Nifti1Image): images = [images]
    mask = numpy.zeros(images[0].shape)
    for image in images: mask[(image.get_data()!=0) * (numpy.isnan(image.get_data()) == False)] += 1
    mask[mask!=len(images)] = 0
    mask[mask==len(images)] = 1
    return mask


'''Resample single image to match some other reference (continuous interpolation, not for atlas)'''
def resample_single_img_ref(image,reference):
  return resample_img(image, target_affine=reference.get_affine(), target_shape=reference.get_shape())


'''Resample multiple image to match some other reference (continuous interpolation, not for atlas)'''
def resample_multi_images_ref(images,mask,resample_dim):
  affine = numpy.diag(resample_dim)
  # Prepare the reference
  reference = nib.load(mask)
  reference_resamp = resample_img(reference, target_affine=affine)
  # Resample images to match reference
  if isinstance(images,str): images = [images]
  images_resamp = []
  for image in images:
    im = nib.load(image)
    images_resamp.append(resample_single_img_ref(im,reference_resamp))
  return images_resamp, reference_resamp

