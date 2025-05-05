#[derive(Debug, PartialEq, Eq)]

pub enum DatasetFormat {
    YOLOObjectDetection,
    YOLOSegmentation,
    YOLOOBB,
    COCOJson,
    PascalVOCXml,
}
