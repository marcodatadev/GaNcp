import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")
    
# -*- coding:utf-8 -*-
import time
import os
import sys
import multiprocessing
from datetime import date
from flask import request, make_response, redirect, render_template,session,flash, url_for
from flaskwebgui import FlaskUI #get the FlaskUI class

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

from app import create_app
from app.forms import SelectionsForm
import Activity_Guide_Changes as agc

app = create_app()


# Feed it the flask app instance 
ui = FlaskUI(app,width=1500,height=800,start_server='flask')


# do your logic as usual in Flask
@app.route('/', methods=["GET", 'POST'])
def index():
    #generate_activity_guides = make_response(redirect('/selections2'))
    return render_template('index.html')

@app.route('/xlsx_file', methods=["GET", 'POST'])
def xlsx_file():
    os.chdir('../')
    xlsx_path = os.getcwd()
    xlsx_path = os.path.join(xlsx_path + "\Activity_Guide_Changes\GaN_cons_and_dates.xlsx")
    os.startfile(xlsx_path)
    os.chdir('main')
    return render_template('index.html')

@app.route('/docx_files', methods=["GET", 'POST'])
def docx_files():
    os.chdir('../')
    docx_path = os.getcwd()
    docx_path = os.path.join(docx_path + "\docs_to_change")
    os.startfile(docx_path)
    os.chdir('main')
    return render_template('index.html')

@app.route('/pdf_files', methods=["GET", 'POST'])
def pdf_files():
    os.chdir('../')
    pdf_path = os.getcwd()
    pdf_path = os.path.join(pdf_path + "\pdf_files")
    os.startfile(pdf_path)
    os.chdir('main')
    return render_template('index.html')   

@app.route('/selections2', methods=["GET", 'POST'])
def selections2():
    selections_form = SelectionsForm()
    selections_form.year.default = date.today().year
    selections_form.process()

    north_consts = session.get('north_consts')
    context = {
        'selections_form': selections_form
        }

    

    if request.method == 'POST':
        year=request.form.get('year')
        north_consts=request.form.getlist('north_consts')
        north_langs=request.form.getlist('north_langs')
        north_lats=request.form.getlist('north_lats')
        south_consts=request.form.getlist('south_consts')
        south_langs=request.form.getlist('south_langs')
        south_lats=request.form.getlist('south_lats')
        download_check = request.form.get('download_charts')
        #select_everything = request.form.get('download_charts')
        if len(north_consts) > 0 and len(north_langs) == 0 and len(north_lats)==0:
            flash('To get an Activity guide for a North Constellation, you must select at least one Constellation, one Language, and one Latitude simultaneously.')
            print(os.getcwd())
            return redirect(url_for('selections2'))
        elif len(north_consts) == 0 and len(north_langs) > 0 and len(north_lats)==0:
            flash('To get an Activity guide for a North Constellation, you must select at least one Constellation, one Language, and one Latitude simultaneously.')
            print(os.getcwd())
            return redirect(url_for('selections2'))
        elif len(north_consts) == 0 and len(north_langs) == 0 and len(north_lats)>0:
            flash('To get an Activity guide for a North Constellation, you must select at least one Constellation, one Language, and one Latitude simultaneously.')
            print(os.getcwd())
            return redirect(url_for('selections2'))

        if len(south_consts) > 0 and len(south_langs) == 0 and len(south_lats)==0:
            flash('To get an Activity guide for a South Constellation, you must select at least one Constellation, one Language, and one Latitude simultaneously.')
            print(os.getcwd())
            return redirect(url_for('selections2'))
        elif len(south_consts) == 0 and len(south_langs) > 0 and len(south_lats)==0:
            flash('To get an Activity guide for a South Constellation, you must select at least one Constellation, one Language, and one Latitude simultaneously.')
            print(os.getcwd())
            return redirect(url_for('selections2'))
        elif len(south_consts) == 0 and len(south_langs) == 0 and len(south_lats)>0:
            flash('To get an Activity guide for a South Constellation, you must select at least one Constellation, one Language, and one Latitude simultaneously.')
            print(os.getcwd())
            return redirect(url_for('selections2'))
        elif len(north_consts) == 0 and len(north_langs) == 0 and len(north_lats)==0 and len(south_consts) == 0 and len(south_langs) == 0 and len(south_lats)==0:
            flash('Please select a North Constellation or a South Constellation.')
            print(os.getcwd())
            return redirect(url_for('selections2'))
        else:
            # Start time counter
            start = time.time()

            #Stablish number of process for multiprocessing
            num_process = 8

            # Activate the Scrapper
            if download_check == None:
                images_downloaded = False
            else:
                images_downloaded = True

            # Get the data from the User for north constellations
            
            north_year = year
            north_constellations = north_consts
            north_languages = north_langs
            latitudes_north = north_lats

            # Get the data from the User for south constellations
            south_year = north_year
            south_constellations = south_consts
            south_languages = south_langs
            latitudes_south = south_lats

            
            # Create the folders for the pdf files
            pdf_folder = agc.create_pdf_folder()
            pdf_north_folders = agc.create_pdf_dir("North", north_year, north_constellations,pdf_folder)
            pdf_south_folders = agc.create_pdf_dir("South", south_year, south_constellations,pdf_folder)

            
            #create the paths for the word files
            north_paths = agc.create_north_paths(pdf_north_folders, north_languages, latitudes_north)
            south_paths = agc.create_south_paths(pdf_south_folders, south_languages, latitudes_south)

            ############################## translations ##########################################
            
            if len(north_constellations) == 0:
                print("There are not constellations selected for the north hemisphere.")
                pass
            else:
                # Create a list from the new doc Paths for a leter use in the Images printing
                north_list_paths = []
                #Call de translation for north constellations function, requiring multiprocessing with Pool
                pool_1 = multiprocessing.Pool(processes = num_process)
                for path in north_paths:
                    north_list_paths.append(pool_1.apply_async(agc.north_translations, args = (path, )).get())
                pool_1.close()
                pool_1.join()
            
            
            # Create a list from the new doc Paths for a leter use in the Images printing
            if len(south_constellations) == 0:
                print("There are not constellations selected for the south hemisphere.")
                pass
            else:
                #Call de translation for north constellations function, requiring multiprocessing with Pool
                south_list_paths = []
                pool_2 = multiprocessing.Pool(processes = num_process)
                for path in south_paths:
                    south_list_paths.append(pool_2.apply_async(agc.south_translations, args = (path, )).get())
                pool_2.close()
                pool_2.join()

            ####################################### Print Charts ##########################################
            if images_downloaded == True:
            
            ################################## Download the Images #########################################
                
                # Activate the Scrapper
                agc.create_image_dir()
                links_north = agc.images_links(north_constellations,latitudes_north)
                links_south = agc.images_links(south_constellations,latitudes_south)
                
                if len(north_constellations) == 0:
                    print("There are not constellations selected for the north hemisphere.")
                    pass
                else: 
                    pool3 = multiprocessing.Pool(processes = num_process)
                    for link in links_north:
                        pool3.apply_async(agc.images_download, args = (link, ))
                    pool3.close()
                    pool3.join()

                
                if len(south_constellations) == 0:
                    print("There are not constellations selected for the south hemisphere.")
                    pass
                else:
                    pool4 = multiprocessing.Pool(processes = num_process)
                    for link in links_south:
                        pool4.apply_async(agc.images_download, args = (link, ))
                    pool4.close()
                    pool4.join()

                ############################# Print Charts Downlaoded in the Word files #####################################

                if len(north_constellations) == 0:
                    print("There are not constellations selected for the north hemisphere.")
                    north_docx_paths = []
                    pass
                else:
                    pool5 = multiprocessing.Pool(processes = num_process)
                    north_docx_paths = []
                    for path in north_list_paths:
                        north_docx_paths.append(pool5.apply_async(agc.print_download_image, args = (path, )).get())
                    pool5.close()
                    pool5.join()
                
                if len(south_constellations) == 0:
                    print("There are not constellations selected for the south hemisphere.")
                    south_docx_paths = []
                    pass
                else:
                    pool6 = multiprocessing.Pool(processes = num_process)
                    south_docx_paths = []
                    for path in south_list_paths:
                        south_docx_paths.append(pool6.apply_async(agc.print_download_image, args = (path, )).get())
                    pool6.close()
                    pool6.join()


            ################################ work with local images ##########################################
            ############################# Print local Charts on the Word files #####################################
            else:
        
                if len(north_constellations) == 0:
                    print("There are not constellations selected for the north hemisphere.")
                    north_docx_paths = []
                    pass
                else:
                    pool5 = multiprocessing.Pool(processes = num_process)
                    north_docx_paths = []
                    for path in north_list_paths:
                        north_docx_paths.append(pool5.apply_async(agc.print_local_image, args = (path, )).get())
                    pool5.close()
                    pool5.join()
                
                if len(south_constellations) == 0:
                    print("There are not constellations selected for the south hemisphere.")
                    south_docx_paths = []
                    pass
                else:
                    pool6 = multiprocessing.Pool(processes = num_process)
                    south_docx_paths = []
                    for path in south_list_paths:
                        south_docx_paths.append(pool6.apply_async(agc.print_local_image, args = (path, )).get())
                    pool6.close()
                    pool6.join()

            ############################# convert .docx to pdf #####################################
            # Creating a List with the word Paths
            if len(north_docx_paths) == 0: 
                total_docx_paths = south_docx_paths
            elif len(south_docx_paths) == 0: 
                total_docx_paths = north_docx_paths
            else:
                total_docx_paths = north_docx_paths + south_docx_paths 

            # converting .docx to pdf
            pool9 = multiprocessing.Pool(processes = num_process)
            results = pool9.map_async(agc.print_pdf, total_docx_paths)
            results.get()

            # Delete the word files
            agc.remove_docs(total_docx_paths)

            os.chdir('main')
            
            # Finishing time counter and getting time of execution
            finish = time.time() - start
            print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(finish)))

            flash("The activity guides are available for use.")
            os.startfile(pdf_folder)

    return render_template('selections2.html', **context)



@app.errorhandler(404)
def not_found(error):

    return render_template('404.html', error=error)



if __name__ =='__main__':

    ui.run()
    

    
