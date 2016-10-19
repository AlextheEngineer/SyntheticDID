
import os
import sys
import cv2
import math
import random
import numpy as np
import numpy.random
import scipy.ndimage


def apply_blur_edges(im, blur_sigma=0.75, blur_width=2):
    '''
    im - image where white (255) indicates background and all other values foreground
    blur_sigma - the strength of bluring used around the edges
    blur_width - number of pixels from the object boundary to blur
    Returns a modification of im, where the background pixels within blur_width of any foreground is blurred
    '''
    # get a mask of foreground pixels in the original image
    original_mask = np.zeros_like(im)
    original_mask[im != 255] = 1

    # blur the whole image
    truncate_param = blur_width / blur_sigma + 1e-4  # truncate param is # of std deviations, not # of pixels
    blurred = scipy.ndimage.gaussian_filter(im, (blur_sigma, blur_sigma), truncate=truncate_param)

    # make the foreground bigger by 
    erode_ele_size = 2 * blur_width + 1  # a square structring element of size 2w+1x2w+1 will erode w pixels
    eroded = scipy.ndimage.grey_erosion(im, size=(erode_ele_size,erode_ele_size))
    eroded_mask = np.zeros_like(eroded)

    # make of only the pixels immediately around the original foreground
    eroded_mask[np.logical_and(eroded != 255, original_mask != 1)] = 2
    out = im * original_mask + eroded_mask * blurred + (1 - (original_mask + eroded_mask)) * 255
    return out


def smoothed_random_field(shape, alpha_min, alpha_max, sigma=2.5):
    field = np.random.uniform(alpha_min, alpha_max, shape)
    smoothed_field = scipy.ndimage.gaussian_filter(field, sigma, truncate=3)
    return smoothed_field


def apply_foreground_noise(im, max_mean=15, max_std=15, sigma=3):
    mean_field = smoothed_random_field(im.shape[:2], -max_mean, max_mean, sigma)
    std_field = smoothed_random_field(im.shape[:2], 0, max_std, sigma)
    noise_field = (std_field * np.random.standard_normal(size=im.shape[:2])) + mean_field

    foreground_mask = np.zeros_like(im)
    foreground_mask[im != 255] = 1
    im = im.astype(int)  # protect against over-flow wrapping if im is uint8
    im = im + noise_field * foreground_mask

    # truncate back to image range
    im = np.clip(im, 0, 255)
    im = im.astype(np.uint8) 
    return im
    

def apply_foreground_color_noise(im):
    b = apply_foreground_noise(im)
    g = apply_foreground_noise(im)
    r = apply_foreground_noise(im)
    return np.concatenate( (b[:,:,np.newaxis], g[:,:,np.newaxis], r[:,:,np.newaxis]), axis=2)


def apply_elastic_deformation(im, alpha=10, sigma=2.5):
    displacement_x = smoothed_random_field(im.shape[:2], -1 * alpha, alpha, sigma)
    displacement_y = smoothed_random_field(im.shape[:2], -1 * alpha, alpha, sigma)

    coords_y = np.asarray( [ [y] * im.shape[1] for y in range(im.shape[0]) ])
    coords_y = np.clip(coords_y + displacement_y, 0, im.shape[0])

    coords_x = np.transpose(np.asarray( [ [x] * im.shape[0] for x in range(im.shape[1]) ] ))
    coords_x = np.clip(coords_x + displacement_x, 0, im.shape[1])

    # the backwards mapping function, which assures that all coords are in
    # the range of the input
    if im.ndim == 3:
        coords_y = coords_y[:,:,np.newaxis]
        coords_y = np.concatenate(im.shape[2] * [coords_y], axis=2)[np.newaxis,:,:,:]

        coords_x = coords_x[:,:,np.newaxis]
        coords_x = np.concatenate(im.shape[2] * [coords_x], axis=2)[np.newaxis,:,:,:]

        coords_d = np.zeros_like(coords_x)
        for x in range(im.shape[2]):
            coords_d[:,:,:,x] = x
        coords = np.concatenate( (coords_y, coords_x, coords_d), axis=0)
    else:
        coords = np.concatenate( (coords_y[np.newaxis,:,:], coords_x[np.newaxis,:,:]), axis=0)

    ## first order spline interpoloation (bilinear?) using the backwards mapping
    output = scipy.ndimage.map_coordinates(im, coords, order=1, mode='reflect')

    return output


def crop_to_foreground(im):
    y, x = np.where(im != 255)
    y_min = np.min(y)
    y_max = np.max(y)
    x_min = np.min(x)
    x_max = np.max(x)
    return im[y_min:y_max,x_min:x_max]


def apply_resize(im, height, width):
    size = (height, width)
    return cv2.resize(im, size)


def apply_color_jitter(im, sigma):
    foreground_mask = np.zeros_like(im)
    foreground_mask[im != 255] = 1
    im = im.astype(int)  # protect against over-flow wrapping if im is uint8
    if im.ndim == 2:
        im = im + foreground_mask * int(np.random.normal(0, sigma))
    else:
        for c in range(im.shape[2]):
            im[:,:,c] = im[:,:,c] + foreground_mask * int(np.random.normal(0, sigma))
    
    # truncate back to image range
    im = np.clip(im, 0, 255)
    im = im.astype(np.uint8) 
    return im

def apply_padding(im):
    n = max(im.shape)
    pad_width = int(n / 2)
    padded = np.pad(im, pad_width=pad_width, mode='constant', constant_values=255)
    return padded
    


def apply_rotation(im, degree):
    center = (im.shape[0] / 2, im.shape[1] / 2)
    rot_mat = cv2.getRotationMatrix2D(center, degree, 1.0)
    padded = apply_padding(im)
    rotated = cv2.warpAffine(padded, rot_mat, (padded.shape[1], padded.shape[0]), flags=cv2.INTER_LINEAR, borderValue=255)
    return crop_to_foreground(rotated)


def apply_shear(im, degree, is_horizontal):
    radians = math.tan(degree * math.pi / 180)
    shear_mat = np.array([ [1, 0, 0], [0, 1, 0] ], dtype=np.float)
    if is_horizontal:
        shear_mat[0,1] = radians
    else:
        shear_mat[1,0] = radians
    padded = apply_padding(im)
    sheared = cv2.warpAffine(padded, shear_mat, (padded.shape[1], padded.shape[0]), flags=cv2.INTER_LINEAR, borderValue=255)
    return crop_to_foreground(sheared)


def apply_perspective(im, p1=None, p2=None, p3=None, p4=None, sigma=5e-4):
    '''
    Applies a general perspective transform to im.  A perspective transform is uniquely defined
        by 4 pairs of points, where one set of 4 define the from coordinates and the other 4 define
        the to coordinates.  This uses the unit square (counter clockwise order) as the from points,
        and the to points are the unit square plus the given points p1-p4 (each a (y,x) tuple or similar)
        E.g. (0,0) -> p1, (1,0) -> (1,0) + p2, etc
    '''
    if not p1:
        p1 = (random.gauss(0, sigma), random.gauss(0, sigma))
    if not p2:
        p2 = (random.gauss(0, sigma), random.gauss(0, sigma))
    if not p3:
        p3 = (random.gauss(0, sigma), random.gauss(0, sigma))
    if not p4:
        p4 = (random.gauss(0, sigma), random.gauss(0, sigma))

    pts1 = np.array([[0,0],[1,0],[1,1],[0,1]], dtype=np.float32)
    pts2 = np.array([  [ 0 + p1[0], 0 + p1[1] ],
                       [ 1 + p2[0], 0 + p2[1] ],
                       [ 1 + p3[0], 1 + p3[1] ],
                       [ 0 + p4[0], 1 + p4[1] ]
                       ], dtype=np.float32)
    M = cv2.getPerspectiveTransform(pts1,pts2)
    padded = apply_padding(im)
    transformed = cv2.warpPerspective(padded, M, (padded.shape[1], padded.shape[0]), borderValue=255)
    return crop_to_foreground(transformed)


def go(im_file, out_dir):
    im = cv2.imread(im_file, 0)
    cv2.imwrite(os.path.join(out_dir, 'original.png'), im)

    cv2.imwrite(os.path.join(out_dir, 'perspective.png'), apply_perspective(im))
    cv2.imwrite(os.path.join(out_dir, 'shear_h.png'), apply_shear(im, 10, True))
    cv2.imwrite(os.path.join(out_dir, 'shear_v.png'), apply_shear(im, 5, False))
    cv2.imwrite(os.path.join(out_dir, 'rotate.png'), apply_rotation(im, 5))
    cv2.imwrite(os.path.join(out_dir, 'elastic.png'), apply_elastic_deformation(im))
    cv2.imwrite(os.path.join(out_dir, 'color_jitter.png'), apply_color_jitter(im, 10))
    cv2.imwrite(os.path.join(out_dir, 'resize.png'), apply_resize(im, 200, 300))
    blurred_edges = apply_blur_edges(im)
    cv2.imwrite(os.path.join(out_dir, 'blur_edges.png'), blurred_edges)
    gray_noised = apply_foreground_noise(blurred_edges)
    cv2.imwrite(os.path.join(out_dir, 'gray_noised.png'), gray_noised)
    color_noised = apply_foreground_color_noise(blurred_edges)
    cv2.imwrite(os.path.join(out_dir, 'color_noised.png'), color_noised)

if __name__ == "__main__":
    go(sys.argv[1], sys.argv[2])


