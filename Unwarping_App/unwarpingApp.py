import sys
sys.dont_write_bytecode = True

from PyQt5.QtWidgets import QWidget, QStackedWidget, QApplication, QLabel, QGridLayout
from PyQt5.QtCore import Qt

from Unwarping_App.pages.p0_landing import LandingPage
from Unwarping_App.pages.p1_provide_transformation import ProvideTransformation
from Unwarping_App.pages.p2_roi_selection import ROISelection
from Unwarping_App.pages.p3_prerun_config import PrerunConfig
from Unwarping_App.pages.p4_sampling_progress import SamplingProgress
from Unwarping_App.pages.p5_sampling_complete import SamplingComplete
from Unwarping_App.pages.p6_checkerboard_detection import CheckerboardDetection
from Unwarping_App.pages.p7_probe_detection import ProbeDetection
from Unwarping_App.pages.p8_transformation_review import TransformationReview



import Unwarping_App.components.utils as utils
from Unwarping_App.components.common import NavBar

from Unwarping_App.services.calibration_service import Transformation

''' Main window for the unwarping section of the application'''
class Main(QWidget):
    def __init__(self, camera, light_connection, printer):
        super().__init__()
        self.camera = camera
        self.light_connection = light_connection
        self.printer = printer
        self.initUI()

    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        screen = QApplication.primaryScreen()
        screen_size = screen.size()

        # Object to store transformation variables
        transformation = Transformation()
        # self.transformation_vars = {
        #     "checkerboard": {
        #         "mtx1": None,
        #         "dist1": None,

        #         "mtx2": None,
        #         "dist2": None,

        #         "size": None,
        #         "location": None,
        #         "image": None,
        #     },
        #     "tags": {
        #         "loc0": None,
        #         "loc1": None,
        #         "loc2": None,
        #         "loc3": None,

        #         "img0": None,
        #         "img1": None,
        #         "img2": None,
        #         "img3": None,

        #         "bottom_left": None,
        #         "top_right": None,

        #         "size": None
        #     },
        #     "probe_offset": None
        # }
        # self.json_path = {
        #     "json": None
        # }

        self.stacked = QStackedWidget()

        # connect pages for application
        self.page0 = LandingPage()
        self.page1 = ProvideTransformation(self.camera,self.light_connection)
        self.page2 = ROISelection()
        self.page3 = PrerunConfig()
        self.page4 = SamplingProgress()
        self.page5 = SamplingComplete()
        self.page6 = CheckerboardDetection(self.camera, self.light_connection, transformation)
        self.page7 = ProbeDetection(self.camera, self.light_connection, transformation)
        self.page8 = TransformationReview(transformation)

        # self.page2.resultAvailable.connect(lambda img: self.page3.receiveResult(img))
        self.page2.photo.roiSignal.connect(lambda dot, rect: self.page3.photo.setVals(dot, rect))
        self.page7.component_tag.offsetAvailable.connect(lambda: self.page8.calculateOffset())

        self.stacked.addWidget(self.page0)
        self.stacked.addWidget(self.page1)
        self.stacked.addWidget(self.page2)
        self.stacked.addWidget(self.page3)
        self.stacked.addWidget(self.page4)
        self.stacked.addWidget(self.page5)
        self.stacked.addWidget(self.page6)
        self.stacked.addWidget(self.page7)
        self.stacked.addWidget(self.page8)

        self.stacked.currentChanged.connect(lambda: self.hide_nav(self.stacked.currentIndex()))
        self.stacked.currentChanged.connect(lambda: self.nav.steps.updateSteps(self.stacked.currentIndex()))

        ''' PAGE CONNECTIONS '''
        # Landing page, manually change stack index for specific workflow
        self.page0.provideTransformation.connect(lambda: self.stacked.setCurrentIndex(1))
        self.page0.createTransformation.connect(lambda: self.stacked.setCurrentIndex(6))

        # Sampling workflow
        self.page1.next.connect(lambda: self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1))
        self.page2.next.connect(lambda: self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1))
        self.page3.next.connect(lambda: self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1))
        self.page4.next.connect(lambda: self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1))

        # Transformation creation workflow
        self.page6.next.connect(lambda: self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1))
        self.page7.next.connect(lambda: self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1))
        

        self.nav = NavBar(self.stacked)
        self.nav.steps.stepClicked.connect(lambda step: self.handleStepClick(step))
        self.nav.hide()

        space = QLabel("")

        self.layout = QGridLayout()
        
        self.layout.addWidget(self.nav, 1, 0,)
        self.layout.addWidget(self.stacked, 2, 0)
        self.layout.addWidget(space, 3, 0, alignment=Qt.AlignCenter)
        
        self.setLayout(self.layout)

        self.setMaximumSize(1440, 851)
        self.setWindowTitle("Unwarping Application")
        self.show()
    

    # Navigate to the appropriate page if the user clicks a number on the nav bar
    def handleStepClick(self, step):
        # Sampling workflow
        if self.stacked.currentIndex() in [1, 2, 3]:
            if step == 1:
                self.stacked.setCurrentIndex(1)
            elif step == 2:
                self.stacked.setCurrentIndex(2)
            else:
                self.stacked.setCurrentIndex(3)

        # Transformation creation workflow
        elif self.stacked.currentIndex() in [6, 7, 8]:
            if step == 1:
                self.stacked.setCurrentIndex(6)
            elif step == 2:
                self.stacked.setCurrentIndex(7)
            else:
                self.stacked.setCurrentIndex(8)
    

    def hide_nav(self, index):
        # Hide/show entire Nav bar
        if index == 0:
            self.nav.hide()
        else:
            self.nav.show() 
        
        # Only hide/show step numbers
        if index in [4, 5]:
            self.nav.steps.hide()
        else:
            self.nav.steps.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    print('Size: %d x %d' % (size.width(), size.height()))
    main_window = Main()
    sys.exit(app.exec_())