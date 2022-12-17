import os
import sys
from pathlib import Path

import cv2
import torch

from database_module import map_service
# limit the number of cpus used by high performance libraries
# os.environ["OMP_NUM_THREADS"] = "1"
# os.environ["OPENBLAS_NUM_THREADS"] = "1"
# os.environ["MKL_NUM_THREADS"] = "1"
# os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
# os.environ["NUMEXPR_NUM_THREADS"] = "1"
from database_module import service

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 strongsort root directory
WEIGHTS = ROOT.parent / 'config/weights'

ROOT_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

print(WEIGHTS)

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

if str(ROOT / 'Yolov5_StrongSORT_OSNet') not in sys.path:
    sys.path.insert(0, str(ROOT / 'Yolov5_StrongSORT_OSNet'))  # add yolov5 ROOT to PATH
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'yolov5') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'yolov5'))  # add yolov5 ROOT to PATH
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'yolov5/utils') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'yolov5/utils'))  # add yolov5 ROOT to PATH
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'yolov5/utils/general') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'yolov5/utils/general'))  # add yolov5 ROOT to PATH
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'strong_sort') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'strong_sort'))  # add strong_sort ROOT to PATH
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'strong_sort/deep/reid') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'strong_sort/deep/reid'))  # add strong_sort ROOT to PATH
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'strong_sort/deep/reid') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'strong_sort/deep/reid'))
if str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'trackers/strong_sort') not in sys.path:
    sys.path.append(str(ROOT / 'Yolov5_StrongSORT_OSNet' / 'trackers/strong_sort'))

ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from Yolov5_StrongSORT_OSNet.yolov5.models.common import DetectMultiBackend
from Yolov5_StrongSORT_OSNet.yolov5.utils.general import (LOGGER, check_img_size, non_max_suppression, scale_boxes,
                                                          xyxy2xywh, strip_optimizer)
from Yolov5_StrongSORT_OSNet.yolov5.utils.torch_utils import select_device, time_sync
from Yolov5_StrongSORT_OSNet.yolov5.utils.plots import Annotator, colors
from dataset import LoadMedia
from Yolov5_StrongSORT_OSNet.trackers.bytetrack.byte_tracker import BYTETracker
from Yolov5_StrongSORT_OSNet.trackers.ocsort.ocsort import OCSort
from Yolov5_StrongSORT_OSNet.trackers.strong_sort.strong_sort import StrongSORT
from Yolov5_StrongSORT_OSNet.trackers.strong_sort.utils.parser import get_config

# remove duplicated stream handler to avoid duplicated logging
# logging.getLogger().removeHandler(logging.getLogger().handlers[0])

from config import provider

detect_conf = provider.get_conf().detect

# def create_flask(var):
#     app = Flask(__name__)
#     port = 8082
#
#     def gen_stream():
#         img = var.value
#         if img is None:
#             return
#         while True:
#             (flag, encodedImage) = cv2.imencode(f".jpg", img)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg' + b'\r\n\r\n' + bytearray(
#                 encodedImage) + b'\r\n')
#
#     @app.get('/stream')
#     def stream():
#         return Response(gen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
#
#     app.run('0.0.0.0', port, debug=True, use_reloader=False)
#
#
# manager = multiprocessing.Manager()
# detect_img = manager.Value('var', None)
#
# multiprocessing.Process(target=create_flask, args=(detect_img,)).start()
config_strongsort = ROOT / 'Yolov5_StrongSORT_OSNet/strong_sort/configs/strong_sort.yaml'


def create_tracker(tracker_type, appearance_descriptor_weights, device, half):
    if tracker_type == 'strongsort':
        # initialize StrongSORT
        cfg = get_config()
        cfg.merge_from_file(config_strongsort)

        strongsort = StrongSORT(
            appearance_descriptor_weights,
            device,
            half,
            max_dist=cfg.STRONGSORT.MAX_DIST,
            max_iou_distance=cfg.STRONGSORT.MAX_IOU_DISTANCE,
            max_age=cfg.STRONGSORT.MAX_AGE,
            max_unmatched_preds=cfg.STRONGSORT.MAX_UNMATCHED_PREDS,
            n_init=cfg.STRONGSORT.N_INIT,
            nn_budget=cfg.STRONGSORT.NN_BUDGET,
            mc_lambda=cfg.STRONGSORT.MC_LAMBDA,
            ema_alpha=cfg.STRONGSORT.EMA_ALPHA,

        )
        return strongsort
    elif tracker_type == 'ocsort':
        ocsort = OCSort(
            det_thresh=0.45,
            iou_threshold=0.2,
            use_byte=False
        )
        return ocsort
    elif tracker_type == 'bytetrack':
        bytetracker = BYTETracker(
            track_thresh=0.6,
            track_buffer=30,
            match_thresh=0.8,
            frame_rate=30
        )
        return bytetracker
    else:
        print('No such tracker')
        exit()


@torch.no_grad()
def run(
        yolo_weights=WEIGHTS / 'yolov5s.pt',  # model.pt path(s),
        strong_sort_weights=WEIGHTS / 'osnet_x0_25_msmt17.pt',  # model.pt path,
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        show_vid=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        save_vid=False,  # save confidences in --save-txt labels
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/track',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        hide_class=False,  # hide IDs
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
):
    # global detect_img

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(yolo_weights, device=device, dnn=dnn, data=None, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    nr_sources = 1

    dataset = LoadMedia(imgsz, stride)

    # Create as many strong sort instances as there are video sources
    strongsort_list = []
    for i in range(nr_sources):
        tracker = create_tracker('strongsort', strong_sort_weights, device, half)
        strongsort_list.append(tracker)
    outputs = [None] * nr_sources

    # Run tracking
    model.warmup(imgsz=(1 if pt else nr_sources, 3, *imgsz))  # warmup
    dt, seen = [0.0, 0.0, 0.0, 0.0], 0
    curr_frames, prev_frames = [None] * nr_sources, [None] * nr_sources
    for frame_idx, (im, im0s, vid_cap) in enumerate(dataset):
        t1 = time_sync()
        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255.0  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        # visualize = increment_path(save_dir / Path(path[0]).stem, mkdir=True) if visualize else False
        pred = model(im, augment=augment, visualize=visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        dt[2] += time_sync() - t3

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            seen += 1
            im0, _ = im0s.copy(), getattr(dataset, 'frame', 0)
            # p = Path(p)  # to Path
            # video file
            # txt_file_name = p.parent.name  # get folder name containing current img
            # save_path = str(save_dir / p.parent.name)  # im.jpg, vid.mp4, ...
            curr_frames[i] = im0

            annotator = Annotator(im0, line_width=2, pil=not ascii)
            if hasattr(strongsort_list[i], 'tracker') and hasattr(strongsort_list[i].tracker, 'camera_update'):
                if prev_frames[i] is not None and curr_frames[i] is not None:  # camera motion compensation
                    strongsort_list[i].tracker.camera_update(prev_frames[i], curr_frames[i])

            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()  # xyxy

                xywhs = xyxy2xywh(det[:, 0:4])
                confs = det[:, 4]
                clss = det[:, 5]

                # pass detections to strongsort
                t4 = time_sync()
                outputs[i] = strongsort_list[i].update(xywhs.cpu(), confs.cpu(), clss.cpu(), im0)
                t5 = time_sync()
                dt[3] += t5 - t4

                # draw boxes for visualization
                if len(outputs[i]) > 0:
                    ids = []
                    db_boxes = []
                    for j, (output, conf) in enumerate(zip(outputs[i], confs)):
                        bboxes = output[0:4]
                        id = output[4]
                        cls = output[5]

                        c = int(cls)  # integer class
                        id = int(id)  # integer id
                        label = None if hide_labels else (f'{id} {names[c]}' if hide_conf else \
                                                              (
                                                                  f'{id} {conf:.2f}' if hide_class else f'{id} {names[c]} {conf:.2f}'))
                        annotator.box_label(bboxes, label, color=colors(c, True))
                        ids.append(id)
                        db_boxes.append({
                            'obj_id': id,
                            'class_name': names[c],
                            'confidence': conf,
                            'x_min': output[0],
                            'y_min': output[0],
                            'x_max': output[0],
                            'y_max': output[0],
                        })

                    service.create_frame(t2, db_boxes)

                map_service.set_detect_benchmark({
                    'yolo_time': t3 - t2,
                    'tracker_time': t5 - t4,
                    'detect_fps': 1 / (t5 - t1),
                })

                LOGGER.info(f'Done. YOLO:({t3 - t2:.3f}s), StrongSORT:({t5 - t4:.3f}s)')

            else:
                strongsort_list[i].increment_ages()
                LOGGER.info('No detections')

            im0 = annotator.result()
            img_name = str(t1) + f'.{detect_conf.image_format}'
            # cv2.imwrite(os.path.join(ROOT_PATH, detect_conf.detect_path, img_name), im0)
            # service.set_detect_image(im0.tobytes())
            map_service.set_detect_image(cv2.imencode(f'.{detect_conf.image_format}', im0)[1].tobytes())
            # detect_img.value = im0

            # service.set_last_detect(img_name)
            # files = os.listdir(os.path.join(ROOT_PATH, detect_conf.detect_path))
            # files.sort(reverse=True)
            # if len(files) > 0:
            #     for file_to_remove in files[int(detect_conf.max_images):]:
            #         os.remove(os.path.join(ROOT_PATH, detect_conf.detect_path, file_to_remove))

            prev_frames[i] = curr_frames[i]

    # Print results
    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(
        f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms strong sort update per image at shape {(1, 3, *imgsz)}' % t)
    # if save_txt or save_vid:
    # s = f"\n{len(list(save_dir.glob('tracks/*.txt')))} tracks saved to {save_dir / 'tracks'}" if save_txt else ''
    # LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(yolo_weights)  # update model (to fix SourceChangeWarning)
