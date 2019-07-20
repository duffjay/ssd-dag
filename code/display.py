import cv2
from utils.utils import load_image_into_numpy_array

BBOX_COLOR = list(
                ((80,80,80),
                (0,120,120),
                (120,120,0),
                (120,0,0),
                (0,120,0),
                (0,0,120),
                (255,0,0),
                (0,255,0),
                (0,0,255),
                (102,0,204),
                (255,102,102),
                (0,0,128))
            )



def inference_to_image(model_type, logger, 
        orig_image_filepath,
        bbox_array, class_id_array, prob_array, 
        model_input_dim, label_dict, prob_threshold):
        
        '''
        1 image
        multiple objects detected - thus arrays of (prob, class_id, bbox)
          Interate through the objects
          display (with bounding box) only images w/ probability > prob_threshold
        '''
        # you need the scale for drawing bounding boxes
        # - we will draw on the ORIGINAL image (e.g. 480x640)
        # - the model input was (300x300 for example)
        # - the inference is normalized for the model input
        # you need to scale back to the original
        orig_image = load_image_into_numpy_array(orig_image_filepath)
        orig_image_width = orig_image.shape[1]
        orig_image_height = orig_image.shape[0]
        objects_per_image_detected = 0
        objects_per_image_ignored = 0
        detected_objects = []                               # empty list of of detected object attributes
        inferences_per_image = prob_array.shape[0]          # how many inferences for this image
        cv2.namedWindow('Object Detect')
        for i in range(inferences_per_image):
                if prob_array[i] > prob_threshold and prob_array[i] <= 1.00:
                    class_id = int(class_id_array[i]) + 1   
                    if model_type == 'tf_lite':
                        # bbox dimensions - note this is not what you think!
                        #    [ymin, xmxin, ymax, xmax]
                        xmin = int(bbox_array[i][1] * orig_image_width)
                        ymin = int(bbox_array[i][0] * orig_image_height)
                        xmax = int(bbox_array[i][3] * orig_image_width)
                        ymax = int(bbox_array[i][2] * orig_image_height)
                    elif model_type == 'edge_tpu':
                        xmin = int(bbox_array[i][0])
                        ymin = int(bbox_array[i][1])
                        xmax = int(bbox_array[i][2])
                        ymax = int(bbox_array[i][3])

                    logger.info("      class: {}-{} prob: {}  bbox: ({},{}), ({},{})".format(
                        class_id, label_dict[class_id], prob_array[i], xmin, ymin, xmax, ymax))
                    # draw the bbox - get the color from global color list
                    cv2.rectangle(orig_image, (xmin,ymin), (xmax, ymax), color=BBOX_COLOR[class_id],thickness=2)
                    # write the class name on the box
                    cv2.putText(orig_image, "{} - {:.2f}".format(label_dict[class_id], prob_array[i]), 
                        (xmin, ymin), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0))
                    # append to detected objects (using this in annotations)
                    detected_objects.append((class_id, label_dict[class_id], prob_array[i], xmin, ymin, xmax, ymax))
                    objects_per_image_detected = objects_per_image_detected + 1
                else:
                    objects_per_image_ignored = objects_per_image_ignored + 1

        logger.info("    obj detected: {}, obj ignored: {}".format(objects_per_image_detected, objects_per_image_ignored))   
        return orig_image, (orig_image_height, orig_image_width), detected_objects