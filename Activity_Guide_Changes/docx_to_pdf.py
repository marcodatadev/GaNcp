import os 
from datetime import datetime
from docx2pdf import convert


# Create the PDF Folder where the new files are going to be created.
def create_pdf_folder():

    current_day_hour = datetime.now()
    save_path = os.getcwd()
    save_path = os.path.join(save_path + "\pdf_files\Activity_Guides_" + current_day_hour.strftime('%Y%m%d_%H%M%S'))
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    return save_path

# Create the folders for each constellation
def create_pdf_dir(cardinal, year, constellations, pdf_folder):
    
    paths = []
    for con in constellations:
        save_path = os.getcwd() 
        save_path = os.path.join(pdf_folder + "\GaN_{cardinal}_{year}_ActivityGuide_{con}".format(cardinal = cardinal, year = year, con = con))
        os.mkdir(save_path)
        paths.append(save_path)

    return paths

#Create the PDF paths in the new folders
def create_pdf_paths(docx_paths, pdf_folders):
    pdf_paths = []
    for pdf_folder in pdf_folders:
        for docx_path in docx_paths:
            constellation = docx_path.split('_')[-4]
            if constellation in pdf_folder:
                docx_path1 = docx_path[:-5]
                docx_path1 = docx_path1.split('\\')[-1]

                pdf_path = os.path.join(pdf_folder + "\\" + docx_path1 +".pdf" )

                pdf_paths.append(pdf_path)
    
    return pdf_paths

#Covert tthe docx files into pdf files
def print_pdf(path):
    
    pdf_path = path.replace(".docx", ".pdf")

    name = pdf_path.split('\\')[-1]

    try:
        convert(path, pdf_path, keep_active= True)        
        
    except Exception as e:
        print(e)
            
    print(name + " has been printed" + "\n__________________________________________________________________\n")
    
    return pdf_path


# remove all the .docx files to deliver the pdfs
def remove_docs(paths):

    for path in paths:
        if path.endswith('.docx'):
            os.remove(path)
            print(".docx file deleted")

    return print("The activity guides are available for use")

