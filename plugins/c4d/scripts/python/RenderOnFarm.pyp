# -*- coding: utf-8 -*-
import c4d
import os
import time

import af

from c4d import gui, plugins, bitmaps

# ------------------------------
# All the IDs for the GUI-Stuff
# ------------------------------
GROUP_ID_TABS = 1001
GROUP_ID_SUBMISSION = 1002
GROUP_ID_SCHEDULING = 1003
GROUP_ID_MASKS = 1004
GROUP_ID_BUTTONS = 1005

CHECKBOX_BAKE_CONSTRAINTS = 1101
CHECKBOX_CREATE_JOB_PAUSED = 1102
CHECKBOX_DO_NOT_COPY_LOCALLY = 1103

BUTTON_CLOSE = 1201
BUTTON_RENDER = 1302

STATIC_TEXT_STARTFRAME = 1301
STATIC_TEXT_ENDFRAME = 1302
STATIC_TEXT_JOB_NAME = 1303
STATIC_TEXT_PRIORITY = 1304
STATIC_TEXT_BY_FRAME = 1305
STATIC_TEXT_FRAMES_PER_TASK = 1306
STATIC_TEXT_MAX_HOSTS = 1307
STATIC_TEXT_MAX_RUNTIME = 1308
STATIC_TEXT_CAPACITY = 1309
STATIC_TEXT_HOSTS_MASK = 1310
STATIC_TEXT_EXCLUDE_HOSTS_MASK = 1311
STATIC_TEXT_DEPEND_MASK = 1312
STATIC_TEXT_DEPEND_MASK_GLOBAL = 1313
STATIC_TEXT_OUTPUT = 1314

TEXTBOX_JOBNAME = 1401
TEXTBOX_HOSTS_MASK = 1402
TEXTBOX_EXCLUDE_HOSTS_MASK = 1403
TEXTBOX_DEPEND_MASK = 1404
TEXTBOX_DEPEND_MASK_GLOBAL = 1405
TEXTBOX_OUTPUT = 1406

EDITSLIDER_STARTFRAME = 1501
EDITSLIDER_ENDFRAME = 1502
EDITSLIDER_PRIORITY = 1503
EDITSLIDER_BY_FRAME = 1504
EDITSLIDER_FRAMES_PER_TASK = 1505
EDITSLIDER_MAX_HOSTS = 1506
EDITSLIDER_MAX_RUNTIME = 1507
EDITSLIDER_CAPACITY = 1508

WINDOW_WIDTH = 320

PLUGIN_ID = 1027905
PLUGIN_ID = 1027909


class RenderSceneWindow(c4d.gui.GeDialog):
    """Missing DocString"""

    def __init__(self, this_parent):
        # Get the Parent-Class and save it as an internal variable
        self.parentClass = this_parent

    def CreateLayout(self):
        """Missing DocString"""
        # Create the layout of the dialog
        self.SetTitle("Export Scene")

        self.TabGroupBegin(GROUP_ID_TABS, c4d.BFH_SCALEFIT, tabtype=c4d.TAB_TABS)

        # ------------------------------
        # START TAB SUBMISSION
        # ------------------------------
        self.GroupBegin(
            GROUP_ID_SUBMISSION, c4d.BFH_SCALEFIT, title="Submission", cols=1
        )

        self.AddStaticText(STATIC_TEXT_JOB_NAME, c4d.BFH_LEFT, name="Job Name:")
        self.AddEditText(TEXTBOX_JOBNAME, c4d.BFH_SCALEFIT)

        self.AddStaticText(STATIC_TEXT_OUTPUT, c4d.BFH_LEFT, name="Overwrite Output:")
        self.AddEditText(TEXTBOX_OUTPUT, c4d.BFH_SCALEFIT)

        self.AddStaticText(STATIC_TEXT_PRIORITY, c4d.BFH_LEFT, name="Priority:")
        self.AddEditSlider(EDITSLIDER_PRIORITY, c4d.BFH_SCALEFIT)

        self.AddStaticText(STATIC_TEXT_STARTFRAME, c4d.BFH_LEFT, name="Framerange:")
        self.AddEditSlider(EDITSLIDER_STARTFRAME, c4d.BFH_SCALEFIT)
        self.AddEditSlider(EDITSLIDER_ENDFRAME, c4d.BFH_SCALEFIT)

        self.AddStaticText(STATIC_TEXT_BY_FRAME, c4d.BFH_LEFT, name="By Frame:")
        self.AddEditSlider(EDITSLIDER_BY_FRAME, c4d.BFH_SCALEFIT)

        self.AddCheckbox(
            CHECKBOX_BAKE_CONSTRAINTS,
            c4d.BFH_FIT,
            name="Bake Constraints",
            initw=WINDOW_WIDTH,
            inith=15,
        )
        self.AddCheckbox(
            CHECKBOX_DO_NOT_COPY_LOCALLY,
            c4d.BFH_FIT,
            name="Do not copy Scene to Hosts",
            initw=WINDOW_WIDTH,
            inith=15,
        )
        self.AddCheckbox(
            CHECKBOX_CREATE_JOB_PAUSED,
            c4d.BFH_FIT,
            name="Create Job Paused",
            initw=WINDOW_WIDTH,
            inith=15,
        )

        self.GroupEnd()  # GROUP_ID_SUBMISSION

        # ------------------------------
        # START TAB SCHEDULING
        # ------------------------------
        self.GroupBegin(
            GROUP_ID_SCHEDULING, c4d.BFH_SCALEFIT, title="Scheduling", cols=1
        )

        self.AddStaticText(
            STATIC_TEXT_FRAMES_PER_TASK, c4d.BFH_LEFT, name="Frames per Task:"
        )
        self.AddEditSlider(EDITSLIDER_FRAMES_PER_TASK, c4d.BFH_SCALEFIT)

        self.AddStaticText(
            STATIC_TEXT_MAX_HOSTS, c4d.BFH_LEFT, name="Max Hosts (Max Running Tasks):"
        )
        self.AddEditSlider(EDITSLIDER_MAX_HOSTS, c4d.BFH_SCALEFIT)

        self.AddStaticText(
            STATIC_TEXT_MAX_RUNTIME, c4d.BFH_LEFT, name="Max Runtime (min):"
        )
        self.AddEditSlider(EDITSLIDER_MAX_RUNTIME, c4d.BFH_SCALEFIT)

        self.AddStaticText(STATIC_TEXT_CAPACITY, c4d.BFH_LEFT, name="Capacity:")
        self.AddEditSlider(EDITSLIDER_CAPACITY, c4d.BFH_SCALEFIT)

        self.GroupEnd()  # GROUP_ID_SCHEDULING

        # ------------------------------
        # START TAB MASKS
        # ------------------------------
        self.GroupBegin(GROUP_ID_MASKS, c4d.BFH_SCALEFIT, title="Masks", cols=1)

        self.AddStaticText(STATIC_TEXT_HOSTS_MASK, c4d.BFH_LEFT, name="Hosts Mask:")
        self.AddEditText(TEXTBOX_HOSTS_MASK, c4d.BFH_SCALEFIT)

        self.AddStaticText(
            STATIC_TEXT_EXCLUDE_HOSTS_MASK, c4d.BFH_LEFT, name="Exclude Hosts Mask:"
        )
        self.AddEditText(TEXTBOX_EXCLUDE_HOSTS_MASK, c4d.BFH_SCALEFIT)

        self.AddStaticText(STATIC_TEXT_DEPEND_MASK, c4d.BFH_LEFT, name="Depend Mask:")
        self.AddEditText(TEXTBOX_DEPEND_MASK, c4d.BFH_SCALEFIT)

        self.AddStaticText(
            STATIC_TEXT_DEPEND_MASK_GLOBAL, c4d.BFH_LEFT, name="Global Depend Mask:"
        )
        self.AddEditText(TEXTBOX_DEPEND_MASK_GLOBAL, c4d.BFH_SCALEFIT)

        self.GroupEnd()  # GROUP_ID_MASKS

        self.GroupEnd()  # GROUP_ID_TABS

        # ------------------------------
        # START BUTTONS
        # ------------------------------
        self.GroupBegin(GROUP_ID_BUTTONS, c4d.BFH_SCALEFIT, cols=2, rows=1)
        self.AddButton(BUTTON_CLOSE, c4d.BFH_SCALE, name="Close")
        self.AddButton(BUTTON_RENDER, c4d.BFH_SCALE, name="Start Render")
        self.GroupEnd()

        return True

    def InitValues(self):
        """Missing DocString"""
        # Get all the values from the parentClass and init everything with it
        self.SetReal(
            EDITSLIDER_STARTFRAME,
            self.parentClass.startFrame,
            min=self.parentClass.startFrame,
            max=self.parentClass.endFrame,
        )
        self.SetReal(
            EDITSLIDER_ENDFRAME,
            self.parentClass.endFrame,
            min=self.parentClass.startFrame,
            max=self.parentClass.endFrame,
        )
        self.SetReal(EDITSLIDER_PRIORITY, self.parentClass.priority, min=-1, max=100)
        self.SetReal(EDITSLIDER_BY_FRAME, self.parentClass.byFrame, min=1, max=100)
        self.SetReal(
            EDITSLIDER_FRAMES_PER_TASK, self.parentClass.framesPerTask, min=1, max=100
        )
        self.SetReal(EDITSLIDER_MAX_HOSTS, self.parentClass.maxHosts, min=-1, max=100)
        self.SetReal(
            EDITSLIDER_MAX_RUNTIME, self.parentClass.maxRuntime, min=-1, max=1000
        )
        self.SetReal(EDITSLIDER_CAPACITY, self.parentClass.capacity, min=-1, max=10000)

        self.SetString(TEXTBOX_JOBNAME, self.parentClass.jobName)
        self.SetString(TEXTBOX_OUTPUT, self.parentClass.output)
        self.SetString(TEXTBOX_HOSTS_MASK, self.parentClass.hostsMask)
        self.SetString(TEXTBOX_EXCLUDE_HOSTS_MASK, self.parentClass.excludeHostsMask)
        self.SetString(TEXTBOX_DEPEND_MASK, self.parentClass.dependMask)
        self.SetString(TEXTBOX_DEPEND_MASK_GLOBAL, self.parentClass.dependMaskGlobal)

        self.SetBool(CHECKBOX_BAKE_CONSTRAINTS, self.parentClass.bakeConstraints)
        self.SetBool(CHECKBOX_CREATE_JOB_PAUSED, self.parentClass.createJobPaused)
        self.SetBool(CHECKBOX_DO_NOT_COPY_LOCALLY, self.parentClass.doNotCopyLocally)

        return True

    def Command(self, id, msg):
        """Missing DocString

        :param id:
        :param msg:
        :return:
        """
        # Handle user input
        if id == BUTTON_CLOSE:
            self.parentClass.startExport = False
            self.Close()

        elif id == BUTTON_RENDER:
            self.parentClass.startFrame = self.GetReal(EDITSLIDER_STARTFRAME)
            self.parentClass.endFrame = self.GetReal(EDITSLIDER_ENDFRAME)
            self.parentClass.priority = self.GetReal(EDITSLIDER_PRIORITY)
            self.parentClass.byFrame = self.GetReal(EDITSLIDER_BY_FRAME)
            self.parentClass.framesPerTask = self.GetReal(EDITSLIDER_FRAMES_PER_TASK)

            self.parentClass.maxHosts = self.GetReal(EDITSLIDER_MAX_HOSTS)
            self.parentClass.maxRuntime = self.GetReal(EDITSLIDER_MAX_RUNTIME)
            self.parentClass.capacity = self.GetReal(EDITSLIDER_CAPACITY)

            self.parentClass.jobName = self.GetString(TEXTBOX_JOBNAME)
            self.parentClass.output = self.GetString(TEXTBOX_OUTPUT)
            self.parentClass.hostsMask = self.GetString(TEXTBOX_HOSTS_MASK)
            self.parentClass.excludeHostsMask = self.GetString(
                TEXTBOX_EXCLUDE_HOSTS_MASK
            )
            self.parentClass.dependMask = self.GetString(TEXTBOX_DEPEND_MASK)
            self.parentClass.dependMaskGlobal = self.GetString(
                TEXTBOX_DEPEND_MASK_GLOBAL
            )

            self.parentClass.bakeConstraints = self.GetBool(CHECKBOX_BAKE_CONSTRAINTS)
            self.parentClass.doNotCopyLocally = self.GetBool(
                CHECKBOX_DO_NOT_COPY_LOCALLY
            )
            self.parentClass.createJobPaused = self.GetBool(CHECKBOX_CREATE_JOB_PAUSED)

            # if (
            #     self.parentClass.output == ""
            #     and not self.parentClass.this_doc.GetActiveRenderData()[
            #         c4d.RDATA_PATH
            #     ].startswith("Output/")
            # ):
            #     c4d.gui.MessageDialog(
            #         "Output-Path is not valid for farm-rendering!!!\n\n"
            #         "To render on the farm you either have to define a full file "
            #         'path in "Overwrite Output" or you have to define in the '
            #         '"Render->Edit Render Settings..->Save->File" a relative Path '
            #         'which starts with "Output/".'
            #     )
            #     return True

            self.parentClass.startExport = True

            self.Close()

        return True


class RenderOnFarm(plugins.CommandData):
    """Missing DocString"""

    def Execute(self, this_doc):
        """Missing DocString

        :param this_doc:
        :return:
        """
        # ------------------------------
        # Here the default-Values can get set
        # ------------------------------

        # Default values of Checkboxes
        self.bakeConstraints = False
        self.createJobPaused = False
        self.doNotCopyLocally = True

        # The default Frame-Range
        self.startFrame = this_doc.GetMinTime().GetFrame(this_doc.GetFps())
        self.endFrame = this_doc.GetMaxTime().GetFrame(this_doc.GetFps())
        self.byFrame = 1

        self.priority = -1
        self.framesPerTask = 1
        self.maxHosts = -1
        self.maxRuntime = -1
        self.capacity = -1

        self.hostsMask = ""
        self.excludeHostsMask = ""
        self.dependMask = ""
        self.dependMaskGlobal = ""

        # ------------------------------
        # Here the Code starts, so no editing after here
        # ------------------------------

        # This variable is to see if the export should start or not when returning
        # from the Gui
        self.startExport = False

        # The Default-Path to export to
        self.tempSceneName = ""  # Gets defined later before it gets saved

        self.thisDoc = this_doc

        self.jobName = self.thisDoc.GetDocumentName()
        self.output = ""  # this_doc.GetActiveRenderData()[c4d.RDATA_PATH]
        self.fileName = self.thisDoc.GetDocumentName()
        self.filePath = self.thisDoc.GetDocumentPath()

        # Check if Scene already got saved
        if self.filePath == "":
            c4d.gui.MessageDialog(
                "Before you can render a Scene on the Farm it has to get " "saved!"
            )
            return True

        par_window = RenderSceneWindow(self)
        par_window.Open(c4d.DLG_TYPE_MODAL, defaultw=WINDOW_WIDTH, defaulth=120)

        if self.startExport:
            if self.bakeConstraints:
                # Clones the current document and sets it active
                temp_doc = self.thisDoc.GetClone()
                c4d.documents.SetActiveDocument(temp_doc)

                # Select all constraint objects and save a list with the
                # Constraints
                constrained_objects = self.SelectConstraintTagObjects(
                    temp_doc, temp_doc.GetFirstObject()
                )

                # Key everything
                self.RecordSelectedObjects(temp_doc, self.startFrame, self.endFrame)

                # Deactivate the Constraints
                self.DeactivateConstraintTags(constrained_objects)
            else:
                temp_doc = self.thisDoc

            if self.bakeConstraints:
                # Save the document
                self.tempSceneName = (
                    "baked_" + str(int(time.time())) + this_doc.GetDocumentName()
                )
                c4d.documents.SaveDocument(
                    temp_doc,
                    os.path.join(self.filePath, self.tempSceneName),
                    c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED,
                    c4d.FORMAT_C4DEXPORT,
                )

                # When scene got saved somewhere else the paths has to get
                # changed
                self.fileName = self.tempSceneName

                # Set the old document active and delete the temp one
                c4d.documents.SetActiveDocument(self.thisDoc)
                c4d.documents.KillDocument(temp_doc)

            self.startFarmRender()

        return True

    def SelectConstraintTagObjects(self, this_doc, obj, constrained_objects=None):
        """Missing DocString

        :param this_doc:
        :param obj:
        :param constrained_objects:
        :return:
        """

        if constrained_objects is None:
            constrained_objects = []

        # Go through all objects and look if they have a Constraint-Tag
        while obj:
            if obj.GetTag(1019364):
                obj.SetBit(c4d.BIT_AOBJ)
                constrained_objects.append(obj)
                print("Constraint-Tag Found on {}".format(obj.GetName()))
            else:
                obj.DelBit(c4d.BIT_AOBJ)

            obj.ClearKeyframeSelection()
            self.SelectConstraintTagObjects(
                this_doc, obj.GetDown(), constrained_objects
            )
            obj = obj.GetNext()

        c4d.EventAdd()

        return constrained_objects

    def RecordSelectedObjects(self, this_doc, start_frame, end_frame):
        """Missing DocString

        :param this_doc:
        :param start_frame:
        :param end_frame:
        :return:
        """
        ctime = this_doc.GetTime()

        for frame in range(start_frame, (end_frame + 1)):
            c4d.StatusSetBar(100 * (frame - start_frame) / (end_frame - start_frame))
            self.setCurrentFrame(frame, this_doc)

            # Record / Set Keyframes
            c4d.CallCommand(12410)

            # Update Timeline
            c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
            print("Baking frame: {}".format(frame))

        print("Everything got baked")

        # Set time Back
        this_doc.SetTime(ctime)
        c4d.EventAdd(c4d.EVENT_ANIMATE)
        c4d.StatusClear()

    def DeactivateConstraintTags(self, constrained_objects):
        """Missing DocString

        :param constrained_objects:
        :return:
        """
        for thisObject in constrained_objects:
            # Disable Constraint-Tag
            thisObject.GetTag(1019364)[c4d.EXPRESSION_ENABLE] = 0
            print("Constraint-Tag got deactivated on {}".format(thisObject.GetName()))

    def setCurrentFrame(self, frame, this_doc):
        """Missing DocString

        :param frame:
        :param this_doc:
        :return:
        """
        this_doc.SetTime(c4d.BaseTime(float(frame) / this_doc.GetFps()))
        this_doc.ExecutePasses(None, True, True, True, 0)
        c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)

    def startFarmRender(self):
        """Missing DocString"""
        scene_path = os.path.join(self.filePath, self.fileName)

        # Create Job:
        job = af.Job(self.fileName)
        job.setPriority(self.priority)
        job.setMaxRunningTasks(self.maxHosts)
        if self.jobName != "":
            job.setName(self.jobName)
        if self.createJobPaused:
            job.setOffline()
        if self.hostsMask != "":
            job.setHostsMask(self.hostsMask)
        if self.excludeHostsMask != "":
            job.setHostsMaskExclude(self.excludeHostsMask)
        if self.dependMask != "":
            job.setDependMask(self.dependMask)
        if self.dependMaskGlobal != "":
            job.setDependMaskGlobal(self.dependMaskGlobal)

        block = af.Block("c4d", "c4d")
        job.blocks.append(block)
        block.setCapacity(self.capacity)
        block.setTasksMaxRunTime(self.maxRuntime * 60)
        block.setNumeric(
            int(self.startFrame),
            int(self.endFrame),
            int(self.framesPerTask),
            int(self.byFrame),
        )

        # c4drender command should get used (which copies all the stuff
        # locally)
        cmd = "c4drender"
        if self.doNotCopyLocally:
            cmd = "c4d"
        cmd += ' -nogui -render "{}" -frame @#@ @#@ {}'.format(scene_path, self.byFrame)
        if self.output != "":
            cmd += ' -oimage "{}"'.format(self.output)
            block.setFiles([self.output])
        block.setCommand(cmd)

        # When Constraints got backed a temp-scene got created and has to be
        # deleted in the end
        if self.bakeConstraints:
            job.setCmdPost('deletefiles "{}"'.format(scene_path))

        # Sending the job to server:
        if not job.send()[0]:
            # If there was a problem tell him what happened
            c4d.gui.MessageDialog("There was a problem with submitting the job.")


# Register the Plugin in C4D
plugins.RegisterCommandPlugin(
    id=PLUGIN_ID,
    str="Render on Farm",
    icon=None,
    help="Sends the current Scene to the Render-Farm",
    info=c4d.OBJECT_GENERATOR,
    dat=RenderOnFarm(),
)
