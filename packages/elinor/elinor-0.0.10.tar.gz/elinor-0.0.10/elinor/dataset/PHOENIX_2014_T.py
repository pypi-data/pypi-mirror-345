# TODO:
import os
import pandas as pd
from typing import List, Generator
from elinor import count_files_by_end
from PIL import Image
# from dataclasses import dataclass
from dataclasses import dataclass
from string import Template
from tqdm import tqdm

@dataclass
class BaseDatasetPhoenix2014TItem:
    frames: Generator
    num: int
    orth: str
    translation: str

TemplateFeatureDir = Template("${root_dir}/features/fullFrame-210x260px/${split}")
TemplateAnnotation = Template("${root_dir}/annotations/manual/PHOENIX-2014-T.${split}.corpus.csv")
TemplateFrame = Template("images${frame}.png")

class BaseDatasetPhoenix2014T(object):
    """Phoenix-2014-T数据集基础类

    数据集结构大致如下：
    PHOENIX-2014-T-release-v3/
    └── PHOENIX-2014-T       <------- ROOT DIR
        ├── annotations
        │   └── manual
        ├── evaluation
        │   ├── sign-recognition
        │   └── sign-translation
        ├── features
        │   └── fullFrame-210x260px
        │       ├── dev
        │       ├── test
        │       └── train
        └── models
            └── languagemodels
    """
    def __init__(
            self, 
            root_dir="./PHOENIX-2014-T",
            split="dev" # train, test, dev
        ):
        self.root_dir=root_dir
        self.features_dir = TemplateFeatureDir.substitute(root_dir=self.root_dir,split=split)
        self.annotations_path = TemplateAnnotation.substitute(root_dir=self.root_dir, split=split)
        self.metadata = self.generate_metadata_from_annotations()


    def __len__(self):
        return len(self.metadata)


    def __getitem__(self, index, path=False):
        metadata = self.metadata.iloc[index]
        frames = self.get_paths_by_dirname(metadata.dirname) if path else self.get_frames_by_dirname(metadata.dirname)
        num = self.metadata.iloc[index].num

        return BaseDatasetPhoenix2014TItem(
            frames=frames,
            num=num,
            orth=metadata.orth,
            translation=metadata.translation
        )


    def generate_metadata_from_annotations(self):
        metadata = pd.read_csv(self.annotations_path, sep="|").rename(columns={"name": "dirname"})
        
        frame_nums = []
        for dirname in metadata.dirname:
            # Check if the directory exists
            dir_path = os.path.join(self.features_dir, dirname)
            frame_num = len([f for f in os.listdir(dir_path) if f.endswith('.png')])
            frame_nums.append(frame_num)
        
        metadata["num"] = frame_nums
        return metadata 
    

    def get_frames_by_dirname(self, dirname) -> Generator:
        video_path = os.path.join(self.features_dir, dirname)
        frame_num = self.metadata[self.metadata["dirname"] == dirname].num.item()
        for i in range(frame_num):
            frame_path = os.path.join(video_path, TemplateFrame.substitute(frame=f"{i+1:04d}"))
            yield Image.open(frame_path)


    def get_paths_by_dirname(self, dirname) -> Generator:
        video_path = os.path.join(self.features_dir, dirname)
        frame_num = self.metadata[self.metadata["dirname"] == dirname].num.item()
        for i in range(frame_num):
            frame_path = os.path.join(video_path, TemplateFrame.substitute(frame=f"{i+1:04d}"))
            yield frame_path

            