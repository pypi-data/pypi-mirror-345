# import os

from PyQt5.QtWidgets import QTabWidget


from ciokatana.v1.Node import ConductorRenderNode
from ciokatana.v1.preview_tab import PreviewTab
from ciokatana.v1.configuration_tab import MainTab
from ciokatana.v1.progress_tab import ProgressTab
from ciokatana.v1.response_tab import ResponseTab
from ciokatana.v1.validation_tab import ValidationTab
from ciokatana.v1 import const as k


class ConductorRenderPanel(QTabWidget):
    def __init__(self, parent, node):
        QTabWidget.__init__(self, parent)
        self.node = node

        self.configuration_tab = MainTab(self)
        self.preview_tab = PreviewTab(self)
        self.validation_tab = ValidationTab(self)
        self.progress_tab = ProgressTab(self)
        self.response_tab = ResponseTab(self)

        self.addTab(self.configuration_tab, k.TAB_NAMES[k.CONFIGURATION_TAB_INDEX])
        self.addTab(self.preview_tab,  k.TAB_NAMES[k.PREVIEW_TAB_INDEX])
        self.addTab(self.validation_tab, k.TAB_NAMES[k.VALIDATION_TAB_INDEX])
        self.addTab(self.progress_tab, k.TAB_NAMES[k.PROGRESS_TAB_INDEX])
        self.addTab(self.response_tab, k.TAB_NAMES[k.RESPONSE_TAB_INDEX])

        self.setTabEnabled(k.VALIDATION_TAB_INDEX, False)
        self.setTabEnabled(k.PROGRESS_TAB_INDEX, False)
        self.setTabEnabled(k.RESPONSE_TAB_INDEX, False) 

        self.configuration_tab.hydrate()
        self.configure_signals()

    def configure_signals(self):
        self.currentChanged.connect(self.on_tab_change)

    def show_validation_tab(self):
        self.setTabEnabled(k.VALIDATION_TAB_INDEX, True)
        self.setCurrentWidget(self.validation_tab)
        
    def show_progress_tab(self):
        self.setTabEnabled(k.PROGRESS_TAB_INDEX, True)
        self.setCurrentWidget(self.progress_tab)

    def show_response_tab(self):
        self.setTabEnabled(k.RESPONSE_TAB_INDEX, True)
        self.setCurrentWidget(self.response_tab)
        

    def on_tab_change(self, index):
        """
        Handle tab change when user clicks  - i.e. preview tab only for now.

        If switching to the preview tab, resolve the submission payload.
        
        """
        if index == k.CONFIGURATION_TAB_INDEX:
            for tab_index in [k.VALIDATION_TAB_INDEX, k.PROGRESS_TAB_INDEX, k.RESPONSE_TAB_INDEX]:
                self.setTabEnabled(tab_index, False)
        elif index == k.PREVIEW_TAB_INDEX:
            self.preview_tab.show_next_job(reset=True)
        elif index == k.PROGRESS_TAB_INDEX:
            pass
        
