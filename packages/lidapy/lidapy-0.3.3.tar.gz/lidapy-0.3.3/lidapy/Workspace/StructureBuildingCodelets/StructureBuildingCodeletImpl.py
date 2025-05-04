from Framework.Tasks.CodeletImpl import CodeletImpl
from Workspace.CurrentSituationalModel.CurrentSituationalModelImpl import \
    CurrentSituationalModelImpl
from Workspace.StructureBuildingCodelets.StructureBuildingCodelet import \
    StructureBuildingCodelet


class StructureBuildingCodeletImpl(StructureBuildingCodelet, CodeletImpl):
    def __init__(self):
        super().__init__()
        self.run_results = None
        self.buffer = CurrentSituationalModelImpl()

    def run(self):
        pass

    def reset(self):
        self.buffer = None
        self.setSoughtContent(None)

    def get_codelet_run_results(self):
        return self.run_results

    def retrieve_workspace_content(self):
        return self.buffer
