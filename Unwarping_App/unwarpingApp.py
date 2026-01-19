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
from Unwarping_App.components.common import NavButtons

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

        # Variables that are used within the application
        # Easier to pass this to multiple pages as one dictionary
        self.transformation_vars = {
            "checkerboard": {
                "mtx1": None,
                "dist1": None,

                "mtx2": None,
                "dist2": None,

                "size": None,
                "location": None,
                "image": None,
            },
            "tags": {
                "loc0": None,
                "loc1": None,
                "loc2": None,
                "loc3": None,

                "img0": None,
                "img1": None,
                "img2": None,
                "img3": None,

                "bottom_left": None,
                "top_right": None,

                "size": None
            },
            "probe_offset": None
        }
        self.json_path = {
            "json": None
        }

        self.stacked = QStackedWidget()

        # connect pages for application
        self.page0 = LandingPage()
        self.page1 = ProvideTransformation()
        self.page2 = ROISelection()
        self.page3 = PrerunConfig()
        self.page4 = SamplingProgress()
        self.page5 = SamplingComplete()
        self.page6 = CheckerboardDetection()
        self.page7 = ProbeDetection()
        self.page8 = TransformationReview()

        self.page2.resultAvailable.connect(lambda img: self.page3.receiveResult(img))

        self.stacked.addWidget(self.page0)
        self.stacked.addWidget(self.page1)
        self.stacked.addWidget(self.page2)
        self.stacked.addWidget(self.page3)
        self.stacked.addWidget(self.page4)
        self.stacked.addWidget(self.page5)
        self.stacked.addWidget(self.page6)
        self.stacked.addWidget(self.page7)
        self.stacked.addWidget(self.page8)

        # Update the page title and hide the next/back buttons if necessary
        self.stacked.currentChanged.connect(lambda: utils.setPageTitle(self.nav, self.stacked.currentIndex()))
        self.stacked.currentChanged.connect(lambda: self.hide_nav(self.stacked.currentIndex()))

        ''' PAGE CONNECTIONS '''
        self.page0.provideTransformation.connect(lambda: self.setPageFromLanding("provide"))
        self.page0.createTransformation.connect(lambda: self.setPageFromLanding("create"))

        ''' LAYOUT SETUP'''
        self.nav = NavButtons(self.stacked)
        self.nav.hide()
        self.nav.back_button.setEnabled(False)
        self.nav.next_button.setEnabled(False)

        space = QLabel("")

        self.layout = QGridLayout()
        
        self.layout.addWidget(self.nav, 1, 0,)
        self.layout.addWidget(self.stacked, 2, 0)
        self.layout.addWidget(space, 3, 0, alignment=Qt.AlignCenter)
        
        self.setLayout(self.layout)

        self.setMaximumSize(1440, 851)
        self.setWindowTitle("Unwarping Application")
        self.show()
    
    # Handle which page to navigate to from the initial page
    def setPageFromLanding(self, selection):
        if selection == "provide":
            self.stacked.setCurrentIndex(1)
            self.nav.back_button.setEnabled(True)
            self.nav.next_button.setEnabled(True)
            self.resize(self.size())
        elif selection == "create":
            self.stacked.setCurrentIndex(6)
            self.nav.back_button.setEnabled(True)
            self.nav.next_button.setEnabled(True)
            self.resize(self.size())
    
    def hide_nav(self, index):
        if index == 0:
            self.nav.hide()
        else:
            self.nav.show() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    print('Size: %d x %d' % (size.width(), size.height()))
    main_window = Main()
    sys.exit(app.exec_())