from ultralytics import YOLO
import sys
import yaml

class TrainerYoloV8():
    def __init__(self, cfg):
        self.cfg = cfg
        self.data = cfg['data']
        self.imgsz = cfg['img_size']
        self.batch = cfg['batch_size']
        self.epochs = cfg['epochs']
        self.output = cfg['output']
        self.mode = cfg['mode']
        self.resume = cfg['resume']

        # loading a pretrained YOLO model
        self.model = YOLO(cfg['model'])

    def train(self):
        results = self.model.train(
            mode=self.mode,
            data=self.data,
            imgsz=self.imgsz,
            epochs=self.epochs,
            batch=self.batch,
            name=self.output,
            resume=self.resume,
        )

    def validate(self):
        results = self.model.val(
            data=self.data,
            imgsz=self.imgsz,
            name=self.output,
        )

with open(sys.argv[1]) as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)

trainer = TrainerYoloV8(cfg)
trainer.train()
trainer.validate()
