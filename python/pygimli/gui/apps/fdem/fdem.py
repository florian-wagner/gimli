# -*- coding: utf-8 -*-

from pygimli.gui.mpl import AppResourceMPL
import pygimli.gui.resources

from pygimli.physics import FDEMData

class FDEMApp(AppResourceMPL):
    """
        Main Class for EM App.

        Default render window is a wxmpl panel
    """
    
    def __init__(self, parent, rendererSlot, propertyInspectorSlot):
        AppResourceWxMPL.__init__(self, parent,
                                  rendererSlot,
                                  propertyInspectorSlot)
        
        # set the name of this application that appears to the resource tree
        self.setName("FDEM")
        
        ## optionaly load content informations for this application, generated by an gui-builder that wrote xrc-files
        ## eg. wxFormBuilder, __file__ is needed to find the xrc-file 
        #self.loadXRC('fdem.xrc', __file__)
        
        #self.mbFDEMData = self.createMainMenu('&FDEM Data')
         
        #### create an item to the Coordinates menu
        #self.createMenuItem(self.mbFDEMData
                                    #, name = "Import File"
                                    #, help = 'auto'
                                    #, function = self.onImportFile)
                                    
        ### the application has some properties that can be altered by the property inspector (PI), loaded and saved
        #self.titleTextProp = self.appendProperty("Title", default = 'unknown', valType = str)
        
        self.fdem = FDEMData()
        
    def createPropertyPanel(self, parent):
        """
         Define and return panel that is shown in the property-inspector (PI) 
         The panel will post created at the first call '
        """

        # create a Notebook for the PI and add the content for the panel with the name piGPSViewerApp defined in gpsview.xrc
        print("panel = self.createPropertyInspectorNoteBookPanel(parent, 'piFDEMApp', title = 'FDEM')")
        panel = self.createPropertyInspectorNoteBookPanel(parent,
                                                          'piFDEMApp',
                                                          title = 'FDEM')
         
        ## bind properties on controls and targetfunctions
        #self.vendorProp.setCtrl(ctrl = wx.xrc.XRCCTRL(panel, 'gpsViewerVendorRadioBox')
                                        #, ctrlEvent = wx.EVT_RADIOBOX
                                        #, targetFunct = self.draw)
                                        
        #self.utmZone.setCtrl(ctrl = wx.xrc.XRCCTRL(panel, 'gpsViewerUTMZone')
                                        #, ctrlEvent = wx.EVT_KILL_FOCUS
                                        #, targetFunct = self.draw)
        #self.ellipsoid.setCtrl(ctrl = wx.xrc.XRCCTRL(panel, 'gpsViewerEllipsoid')
                                        #, ctrlEvent = wx.EVT_KILL_FOCUS
                                        #, targetFunct = self.draw)
                                       
        return panel

    def drawData_(self):
        """
            Define what we have to be drawn (needed from base class) is called
            while a draw event is fired.
        """
        
        #self.axes.grid()
        
       
    def openFile(self, files = None):
        """
            Load data here.
        """
        print("#openFile(self, files = None)")
        self.draw()
    
    def onImportFile(self, event = None):
        """
            Import coordinates in Lon Lat format.
        """
        print("#onImportFile(self, event = None):")
        #self.parent.onOpenFileDialog()
    
