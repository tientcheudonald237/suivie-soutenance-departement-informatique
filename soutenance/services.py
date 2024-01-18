

def get_parents_folder(folder):
    parent_folders = []
    current_folder = folder.parent_folder

    while current_folder is not None:
        parent_folders.insert(0, current_folder)  
        current_folder = current_folder.parent_folder

    return parent_folders

def get_parents_document(document):
    parent_folders = []
    current_folder = document.folder

    while current_folder is not None:
        parent_folders.insert(0, current_folder)  
        current_folder = current_folder.parent_folder

    return parent_folders