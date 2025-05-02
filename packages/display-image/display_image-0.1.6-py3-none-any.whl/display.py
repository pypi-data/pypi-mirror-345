"""
PyQt6 First example display image

In this example, we create a simple
window in PyQt6.

Author: Yuan SUN
"""

import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout,
                             QTabWidget, QFrame, QGroupBox, QScrollArea,
                             QLabel, QGridLayout, QMessageBox, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem)
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from cxx_image_io import read_image, PixelRepresentation, PixelType
import argparse
import pathlib
import numpy as np
import qdarkstyle


class ImageViewer(QGraphicsView):

    def __init__(self, image, metadata, pixelStatus, zoomStatus):
        super().__init__()
        self.image = image
        self.metadata = metadata
        self.pixelStatus = pixelStatus
        self.zoomStatus = zoomStatus
        self.scale_percentage = 100
        qimage = self.convertNumpyArrayToQImage(self.image, self.metadata)
        self.pix_map_image = QPixmap.fromImage(qimage)

        # 创建场景
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 加载图片
        self.image_item = QGraphicsPixmapItem(self.pix_map_image)
        self.scene.addItem(self.image_item)

        # 设置抗锯齿和插值模式
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)  # 以鼠标位置为缩放中心
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # 缩放参数
        self.scale_factor = 1.0  # 当前缩放比例
        self.zoom_history = [1.0]  # **存储缩放比例的历史**
        self.zoom_images = [self.pix_map_image]  # **存储不同缩放比例的图像**
        self.max_zoom = 10.0
        self.min_zoom = 0.1

    def convertNumpyArrayToQImage(self, img, metadata):
        if metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT8:
            image = np.array(img)
            if metadata.fileInfo.pixelType in [
                    PixelType.BAYER_RGGB, PixelType.BAYER_BGGR,
                    PixelType.BAYER_GRBG, PixelType.BAYER_GBRG
            ] or metadata.fileInfo.pixelType == PixelType.GRAYSCALE:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_Grayscale8)
            elif metadata.fileInfo.pixelType == PixelType.RGB:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_RGB888)
            elif metadata.fileInfo.pixelType == PixelType.RGBA:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_RGBA8888)
            else:
                QMessageBox.critical(
                    None, "Error",
                    "Unsupported pixel type  on 8 bits: {} ".format(
                        metadata.fileInfo.pixelType))

        elif (metadata.fileInfo.pixelRepresentation ==
              PixelRepresentation.UINT16):
            factor = 1
            if metadata.fileInfo.pixelPrecision:
                factor = int(65535.0 /
                             (2**metadata.fileInfo.pixelPrecision - 1))
            image = np.array(img * factor)
            if metadata.fileInfo.pixelType in [
                    PixelType.BAYER_RGGB, PixelType.BAYER_BGGR,
                    PixelType.BAYER_GRBG, PixelType.BAYER_GBRG
            ] or metadata.fileInfo.pixelType == PixelType.GRAYSCALE:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_Grayscale16)
            elif metadata.fileInfo.pixelType == PixelType.RGBA:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_RGBA64)
            else:
                QMessageBox.critical(
                    None, "Error",
                    "Unsupported pixel type  on 16 bits: {} ".format(
                        metadata.fileInfo.pixelType))

        else:
            QMessageBox.critical(
                None, "Error", "Unsupported pixel representation: {} ".format(
                    metadata.fileInfo.pixelRepresentation))

    def wheelEvent(self, event):
        """鼠标滚轮事件：允许从 `1.0x` 开始缩小，并记录历史"""
        zoom_in_factor = 1.2
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:  # 滚轮向上，放大
            new_scale = self.scale_factor * zoom_in_factor
            if new_scale <= self.max_zoom:  # 限制最大缩放
                self.scale_factor = new_scale
                self.zoom_history.append(self.scale_factor)  # **记录历史缩放比例**
                self.scale(zoom_in_factor, zoom_in_factor)

        elif event.angleDelta().y() < 0:  # 滚轮向下，缩小
            new_scale = self.scale_factor * zoom_out_factor
            if new_scale >= self.min_zoom:  # 限制最小缩放
                self.scale_factor = new_scale
                self.zoom_history.append(self.scale_factor)  # **记录历史缩放比例**
                self.scale(zoom_out_factor, zoom_out_factor)

        # **如果缩放比例变回 `1.0x`，恢复原图**
        if self.scale_factor == 1.0:
            self.resetTransform()  # **重置所有缩放**
            self.image_item.setPixmap(self.pix_map_image)  # **恢复原图**
            self.zoom_history = [1.0]  # **重置缩放历史**

        scale_percentage = self.scale_factor * 100
        zoom_status = "Zoom factor: {:.1f}%".format(scale_percentage)
        self.zoomStatus.setText(zoom_status)

    def update_coordinates(self, event):
        scene_pos = self.mapToScene(event.pos())  # 转换为场景坐标
        item_pos = self.image_item.mapFromScene(scene_pos)  # 转换为图像坐标

        pix_x = int(item_pos.x())
        pix_y = int(item_pos.y())

        if pix_x >= 0 and pix_x < self.image.shape[
                1] and pix_y >= 0 and pix_y < self.image.shape[0]:
            pixel_value = self.image[pix_y, pix_x]
            pixel_status = "Position：x = {}, y = {}, value = {}".format(
                pix_x, pix_y, pixel_value)
            self.pixelStatus.setText(pixel_status)

    def mousePressEvent(self, event):
        self.update_coordinates(event)


class ImageDisplayer(QWidget):
    image = None
    metadata = None
    image_path = None
    frame = None
    tabWidget = None
    imageArea = None

    def __init__(self, image, metadata, image_path):
        super().__init__()
        self.image = image
        self.metadata = metadata
        self.image_path = image_path
        self.initUI()
        self.showImage()
        self.showMetadata()

    def initImageViewUI(self):
        self.tabWidget = QTabWidget(self)
        self.tabImage = QWidget(self.tabWidget)
        self.tabWidget.addTab(self.tabImage, str(self.image_path))
        self.imageArea = QScrollArea(self.tabImage)
        vbox = QVBoxLayout(self.tabImage)
        vbox.addWidget(self.imageArea)
        self.imageArea.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hbox = QHBoxLayout()
        self.pixelStatus = QLabel("Click pixel to display value", self)
        self.zoomStatus = QLabel("Zoom factor: 100%", self)
        hbox.addWidget(self.pixelStatus)
        hbox.addWidget(self.zoomStatus)
        vbox.addLayout(hbox)


    def initFileInfoUI(self, tabFileInfo):

        labfileFormat = QLabel("fileFormat", tabFileInfo)
        self.labfileFormatValue = QLabel(tabFileInfo)
        labpixelRepresentation = QLabel("pixelRepresentation", tabFileInfo)
        self.labpixelRepresentationValue = QLabel(tabFileInfo)
        labimageLayout = QLabel("imageLayout", tabFileInfo)
        self.labimageLayoutValue = QLabel(tabFileInfo)
        labpixelType = QLabel("pixelType", tabFileInfo)
        self.labpixelTypeValue = QLabel(tabFileInfo)
        labpixelPrecision = QLabel("pixelPrecision", tabFileInfo)
        self.labpixelPrecisionValue = QLabel(tabFileInfo)
        labwidth = QLabel("width", tabFileInfo)
        self.labwidthValue = QLabel(tabFileInfo)
        labheight = QLabel("height", tabFileInfo)
        self.labheightValue = QLabel(tabFileInfo)
        labwidthAlignment = QLabel("widthAlignment", tabFileInfo)
        self.labwidthAlignmentValue = QLabel(tabFileInfo)
        labheightAlignment = QLabel("heightAlignment", tabFileInfo)
        self.labheightAlignmentValue = QLabel(tabFileInfo)
        labsizeAlignment = QLabel("sizeAlignment", tabFileInfo)
        self.labsizeAlignmentValue = QLabel(tabFileInfo)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labfileFormat, 0, 0)
        grid_layout.addWidget(self.labfileFormatValue, 0, 1)
        grid_layout.addWidget(labpixelRepresentation, 1, 0)
        grid_layout.addWidget(self.labpixelRepresentationValue, 1, 1)
        grid_layout.addWidget(labimageLayout, 2, 0)
        grid_layout.addWidget(self.labimageLayoutValue, 2, 1)
        grid_layout.addWidget(labpixelType, 3, 0)
        grid_layout.addWidget(self.labpixelTypeValue, 3, 1)
        grid_layout.addWidget(labpixelPrecision, 4, 0)
        grid_layout.addWidget(self.labpixelPrecisionValue, 4, 1)
        grid_layout.addWidget(labwidth, 5, 0)
        grid_layout.addWidget(self.labwidthValue, 5, 1)
        grid_layout.addWidget(labheight, 6, 0)
        grid_layout.addWidget(self.labheightValue, 6, 1)
        grid_layout.addWidget(labwidthAlignment, 7, 0)
        grid_layout.addWidget(self.labwidthAlignmentValue, 7, 1)
        grid_layout.addWidget(labheightAlignment, 8, 0)
        grid_layout.addWidget(self.labheightAlignmentValue, 8, 1)
        grid_layout.addWidget(labsizeAlignment, 9, 0)
        grid_layout.addWidget(self.labsizeAlignmentValue, 9, 1)

        grid_layout.setRowStretch(grid_layout.rowCount(), 1)

        tabFileInfo.setLayout(grid_layout)

    def initExifUI(self, tabExif):
        labimageWidth = QLabel("imageWidth", tabExif)
        self.labimageWidthValue = QLabel(tabExif)
        labimageHeight = QLabel("imageHeight", tabExif)
        self.labimageHeightValue = QLabel(tabExif)
        labimageDescription = QLabel("imageDescription", tabExif)
        self.labimageDescriptionValue = QLabel(tabExif)
        labmake = QLabel("make", tabExif)
        self.labmakeValue = QLabel(tabExif)
        labmodel = QLabel("model", tabExif)
        self.labmodelValue = QLabel(tabExif)
        laborientation = QLabel("orientation", tabExif)
        self.laborientationValue = QLabel(tabExif)
        labsoftware = QLabel("software", tabExif)
        self.labsoftwareValue = QLabel(tabExif)
        labexposureTime = QLabel("exposureTime", tabExif)
        self.labexposureTimeValue = QLabel(tabExif)
        labfNumber = QLabel("fNumber", tabExif)
        self.labfNumberValue = QLabel(tabExif)
        labisoSpeedRatings = QLabel("isoSpeedRatings", tabExif)
        self.labisoSpeedRatingsValue = QLabel(tabExif)
        labdateTimeOriginal = QLabel("dateTimeOriginal", tabExif)
        self.labdateTimeOriginalValue = QLabel(tabExif)
        labbrightnessValue = QLabel("brightnessValue", tabExif)
        self.labbrightnessValueValue = QLabel(tabExif)
        labexposureBiasValue = QLabel("exposureBiasValue", tabExif)
        self.labexposureBiasValueValue = QLabel(tabExif)
        labfocalLength = QLabel("focalLength", tabExif)
        self.labfocalLengthValue = QLabel(tabExif)
        labfocalLengthIn35mmFilm = QLabel("focalLengthIn35mmFilm", tabExif)
        self.labfocalLengthIn35mmFilmValue = QLabel(tabExif)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labimageWidth, 0, 0)
        grid_layout.addWidget(self.labimageWidthValue, 0, 1)
        grid_layout.addWidget(labimageHeight, 1, 0)
        grid_layout.addWidget(self.labimageHeightValue, 1, 1)
        grid_layout.addWidget(labimageDescription, 2, 0)
        grid_layout.addWidget(self.labimageDescriptionValue, 2, 1)
        grid_layout.addWidget(labmake, 3, 0)
        grid_layout.addWidget(self.labmakeValue, 3, 1)
        grid_layout.addWidget(labmodel, 4, 0)
        grid_layout.addWidget(self.labmodelValue, 4, 1)
        grid_layout.addWidget(laborientation, 5, 0)
        grid_layout.addWidget(self.laborientationValue, 5, 1)
        grid_layout.addWidget(labsoftware, 6, 0)
        grid_layout.addWidget(self.labsoftwareValue, 6, 1)
        grid_layout.addWidget(labexposureTime, 7, 0)
        grid_layout.addWidget(self.labexposureTimeValue, 7, 1)
        grid_layout.addWidget(labfNumber, 8, 0)
        grid_layout.addWidget(self.labfNumberValue, 8, 1)
        grid_layout.addWidget(labisoSpeedRatings, 9, 0)
        grid_layout.addWidget(self.labisoSpeedRatingsValue, 9, 1)
        grid_layout.addWidget(labdateTimeOriginal, 10, 0)
        grid_layout.addWidget(self.labdateTimeOriginalValue, 10, 1)
        grid_layout.addWidget(labbrightnessValue, 11, 0)
        grid_layout.addWidget(self.labbrightnessValueValue, 11, 1)
        grid_layout.addWidget(labexposureBiasValue, 12, 0)
        grid_layout.addWidget(self.labexposureBiasValueValue, 12, 1)
        grid_layout.addWidget(labfocalLength, 13, 0)
        grid_layout.addWidget(self.labfocalLengthValue, 13, 1)
        grid_layout.addWidget(labfocalLengthIn35mmFilm, 14, 0)
        grid_layout.addWidget(self.labfocalLengthIn35mmFilmValue, 14, 1)
        grid_layout.setRowStretch(grid_layout.rowCount(), 1)
        tabExif.setLayout(grid_layout)

    def initCalibrationDataUI(self, tabCalibrationData):

        labblackLevel = QLabel("blackLevel", tabCalibrationData)
        self.labblackLevelValue = QLabel(tabCalibrationData)
        labwhiteLevel = QLabel("whiteLevel", tabCalibrationData)
        self.labwhiteLevelValue = QLabel(tabCalibrationData)
        labcolorMatrix = QLabel("colorMatrix", tabCalibrationData)
        self.labcolorMatrixValue = QLabel(tabCalibrationData)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labblackLevel, 0, 0)
        grid_layout.addWidget(self.labblackLevelValue, 0, 1)
        grid_layout.addWidget(labwhiteLevel, 1, 0)
        grid_layout.addWidget(self.labwhiteLevelValue, 1, 1)
        grid_layout.addWidget(labcolorMatrix, 2, 0)
        grid_layout.addWidget(self.labcolorMatrixValue, 2, 1)

        grid_layout.setRowStretch(grid_layout.rowCount(), 1)

        tabCalibrationData.setLayout(grid_layout)

    def initCameraControlUI(self, tabCameraControl):

        labbwhiteBalance = QLabel("whiteBalance", tabCameraControl)
        self.labwhiteBalanceValue = QLabel(tabCameraControl)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labbwhiteBalance, 0, 0)
        grid_layout.addWidget(self.labwhiteBalanceValue, 0, 1)
        grid_layout.setRowStretch(grid_layout.rowCount(), 1)

        tabCameraControl.setLayout(grid_layout)

    def initLibRawParamsUI(self, tabLibRawParams):

        labrawWidth = QLabel("rawWidth", tabLibRawParams)
        self.labrawWidthValue = QLabel(tabLibRawParams)

        labrawHeight = QLabel("rawHeight", tabLibRawParams)
        self.labrawHeightValue = QLabel(tabLibRawParams)

        labrawWidthVisible = QLabel("rawWidthVisible", tabLibRawParams)
        self.labrawWidthVisibleValue = QLabel(tabLibRawParams)

        labrawHeightVisible = QLabel("rawHeightVisible", tabLibRawParams)
        self.labrawHeightVisibleValue = QLabel(tabLibRawParams)

        labtopMargin = QLabel("topMargin", tabLibRawParams)
        self.labtopMarginValue = QLabel(tabLibRawParams)

        lableftMargin = QLabel("leftMargin", tabLibRawParams)
        self.lableftMarginValue = QLabel(tabLibRawParams)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labrawWidth, 0, 0)
        grid_layout.addWidget(self.labrawWidthValue, 0, 1)
        grid_layout.addWidget(labrawHeight, 1, 0)
        grid_layout.addWidget(self.labrawHeightValue, 1, 1)
        grid_layout.addWidget(labrawWidthVisible, 2, 0)
        grid_layout.addWidget(self.labrawWidthVisibleValue, 2, 1)
        grid_layout.addWidget(labrawHeightVisible, 3, 0)
        grid_layout.addWidget(self.labrawHeightVisibleValue, 3, 1)
        grid_layout.addWidget(labtopMargin, 4, 0)
        grid_layout.addWidget(self.labtopMarginValue, 4, 1)
        grid_layout.addWidget(lableftMargin, 5, 0)
        grid_layout.addWidget(self.lableftMarginValue, 5, 1)

        grid_layout.setRowStretch(grid_layout.rowCount(), 1)

        tabLibRawParams.setLayout(grid_layout)

    def initMetadataUI(self):
        self.frame = QFrame(self)
        framelayout = QVBoxLayout(self.frame)
        groupbox = QGroupBox("Image Metadata", self.frame)
        grouplayout = QVBoxLayout(groupbox)
        tabWidgetMeta = QTabWidget(groupbox)

        tabFileInfo = QWidget(tabWidgetMeta)
        tabExif = QWidget(tabWidgetMeta)
        tabCalibrationData = QWidget(tabWidgetMeta)
        tabCameraControl = QWidget(tabWidgetMeta)
        tabLibRawParams = QWidget(tabWidgetMeta)

        tabWidgetMeta.addTab(tabFileInfo, "FileInfo")
        tabWidgetMeta.addTab(tabExif, "Exif")
        tabWidgetMeta.addTab(tabCalibrationData, "CalibrationData")
        tabWidgetMeta.addTab(tabCameraControl, "CameraControl")
        tabWidgetMeta.addTab(tabLibRawParams, "LibRawParams")

        self.initFileInfoUI(tabFileInfo)
        self.initExifUI(tabExif)
        self.initCalibrationDataUI(tabCalibrationData)
        self.initCameraControlUI(tabCameraControl)
        self.initLibRawParamsUI(tabLibRawParams)

        grouplayout.addWidget(tabWidgetMeta)
        groupbox.setLayout(grouplayout)

        imv = pg.ImageView()
        imv.ui.roiBtn.hide()
        imv.ui.menuBtn.hide()
        fileInfo = self.metadata.fileInfo.serialize()
        imv.setImage(self.image,
                     xvals=np.linspace(0., fileInfo['pixelPrecision'],
                                       self.image.shape[0]))

        hist = pg.HistogramLUTWidget(orientation='horizontal')
        hist.setImageItem(imv.getImageItem())

        groupboxHist = QGroupBox("Histogram", self.frame)
        grouplayoutHist = QVBoxLayout(groupboxHist)
        grouplayoutHist.addWidget(hist)

        framelayout.addWidget(groupbox)
        framelayout.addWidget(groupboxHist)
        self.frame.setLayout(framelayout)

    def initUI(self):
        self.initImageViewUI()
        self.initMetadataUI()

        hbox = QHBoxLayout()

        hbox.addWidget(self.tabWidget)
        hbox.addWidget(self.frame)
        hbox.setStretchFactor(self.tabWidget, 4)
        hbox.setStretchFactor(self.frame, 1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('Image Displayer')

    def showImage(self):
        self.image_viewer = ImageViewer(self.image, self.metadata,
                                        self.pixelStatus, self.zoomStatus)
        self.imageArea.setWidget(self.image_viewer)
        self.imageArea.setWidgetResizable(True)
        self.tabWidget.setCurrentIndex(0)

    def showMetadata(self):
        fileInfo = self.metadata.fileInfo.serialize()
        if 'fileFormat' in fileInfo:
            self.labfileFormatValue.setText(fileInfo['fileFormat'])
        if 'pixelRepresentation' in fileInfo:
            self.labpixelRepresentationValue.setText(
                fileInfo['pixelRepresentation'])
        if 'imageLayout' in fileInfo:
            self.labimageLayoutValue.setText(fileInfo['imageLayout'])
        if 'pixelType' in fileInfo:
            self.labpixelTypeValue.setText(fileInfo['pixelType'])
        if 'pixelPrecision' in fileInfo:
            self.labpixelPrecisionValue.setText(str(
                fileInfo['pixelPrecision']))
        if 'width' in fileInfo:
            self.labwidthValue.setText(str(fileInfo['width']))
        if 'height' in fileInfo:
            self.labheightValue.setText(str(fileInfo['height']))
        if 'widthAlignment' in fileInfo:
            self.labwidthAlignmentValue.setText(str(
                fileInfo['widthAlignment']))
        if 'heightAlignment' in fileInfo:
            self.labheightAlignmentValue.setText(
                str(fileInfo['heightAlignment']))
        if 'sizeAlignment' in fileInfo:
            self.labsizeAlignmentValue.setText(str(fileInfo['sizeAlignment']))

        exifMetadata = self.metadata.exifMetadata.serialize()
        if 'imageWidth' in exifMetadata:
            self.labimageWidthValue.setText(str(exifMetadata['imageWidth']))
        if 'imageHeight' in exifMetadata:
            self.labimageHeightValue.setText(str(exifMetadata['imageHeight']))
        if 'imageDescription' in exifMetadata:
            self.labimageDescriptionValue.setText(
                str(exifMetadata['imageDescription']))
        if 'make' in exifMetadata:
            self.labmakeValue.setText(str(exifMetadata['make']))
        if 'model' in exifMetadata:
            self.labmodelValue.setText(str(exifMetadata['model']))

        if 'orientation' in exifMetadata:
            self.laborientationValue.setText(str(exifMetadata['orientation']))
        if 'software' in exifMetadata:
            self.labsoftwareValue.setText(str(exifMetadata['software']))
        if 'exposureTime' in exifMetadata:
            self.labexposureTimeValue.setText(str(
                exifMetadata['exposureTime']))
        if 'fNumber' in exifMetadata:
            self.labfNumberValue.setText(str(exifMetadata['fNumber']))
        if 'isoSpeedRatings' in exifMetadata:
            self.labisoSpeedRatingsValue.setText(
                str(exifMetadata['isoSpeedRatings']))
        if 'dateTimeOriginal' in exifMetadata:
            self.labdateTimeOriginalValue.setText(
                str(exifMetadata['dateTimeOriginal']))
        if 'brightnessValue' in exifMetadata:
            self.labbrightnessValueValue.setText(
                str(exifMetadata['brightnessValue']))

        if 'exposureBiasValue' in exifMetadata:
            self.labexposureBiasValueValue.setText(
                str(exifMetadata['exposureBiasValue']))
        if 'focalLength' in exifMetadata:
            self.labfocalLengthValue.setText(str(exifMetadata['focalLength']))
        if 'focalLengthIn35mmFilm' in exifMetadata:
            self.labfocalLengthIn35mmFilmValue.setText(
                str(exifMetadata['focalLengthIn35mmFilm']))

        calibrationData = self.metadata.calibrationData.serialize()
        if 'blackLevel' in calibrationData:
            self.labblackLevelValue.setText(str(calibrationData['blackLevel']))
        if 'whiteLevel' in calibrationData:
            self.labwhiteLevelValue.setText(str(calibrationData['whiteLevel']))
        if 'colorMatrix' in calibrationData:
            self.labcolorMatrixValue.setText(
                str(calibrationData['colorMatrix']))
            self.labcolorMatrixValue.setWordWrap(True)

        cameraControls = self.metadata.cameraControls.serialize()
        if 'whiteBalance' in cameraControls:
            self.labwhiteBalanceValue.setText(
                str(cameraControls['whiteBalance']))
            self.labwhiteBalanceValue.setWordWrap(True)

        if self.metadata.libRawParameters:
            libRawParams = self.metadata.libRawParameters.__dict__
            if 'rawWidth' in libRawParams:
                self.labrawWidthValue.setText(str(libRawParams['rawWidth']))
            if 'rawHeight' in libRawParams:
                self.labrawHeightValue.setText(str(libRawParams['rawHeight']))
            if 'rawWidthVisible' in libRawParams:
                self.labrawWidthVisibleValue.setText(
                    str(libRawParams['rawWidthVisible']))
            if 'rawHeightVisible' in libRawParams:
                self.labrawHeightVisibleValue.setText(
                    str(libRawParams['rawHeightVisible']))
            if 'topMargin' in libRawParams:
                self.labtopMarginValue.setText(str(libRawParams['topMargin']))
            if 'leftMargin' in libRawParams:
                self.lableftMarginValue.setText(str(
                    libRawParams['leftMargin']))


def parse_command_line(argv):
    parser = argparse.ArgumentParser(
        description='Display image and metadata.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-i',
                               '--image',
                               required=True,
                               type=str,
                               help='Path to image file')

    parser.add_argument('-m',
                        '--metadata',
                        type=str,
                        default=None,
                        help='Path to image metadata sidecar file.')
    return parser.parse_args(argv)


def main():
    args = parse_command_line(sys.argv[1:])

    try:
        image_path = pathlib.Path(args.image)
        assert image_path.exists(), 'Non-existing image path: {}'.format(
            str(image_path))
        if args.metadata:
            metadata_path = pathlib.Path(args.metadata)
            assert metadata_path.exists(
            ), 'Non-existing metadata path: {}'.format(str(metadata_path))
        else:
            metadata_path = None
        image, metadata = read_image(image_path, metadata_path)

        app = QApplication(sys.argv)
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt6()
        app.setStyleSheet(dark_stylesheet)
        img_displayer = ImageDisplayer(image, metadata, image_path)
        img_displayer.resize(1000, 800)
        img_displayer.move(100, 100)
        img_displayer.show()
    except Exception as e:
        sys.exit("Exception caught in display image, check the error log: {}.".
                 format(str(e)))
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
