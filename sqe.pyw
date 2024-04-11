#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#          Wildfly Server Automation   #
#                    *                 #
#          Script By Sajin Sabu        #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


## Wildfly Configurations ##

wildfly_dir = "E:\\sme\\server\\"
python_log_dir = "E:\\sme\\pythonscriptsdemo\\"
backup_dir = "E:\\sme\\backup\\"
app_log_dir = "E:\\sme\\logs\\"
props_dir = "E:\\sme\\proptrunk\\"
ip = "localhost"

## Mail Server Configuration ##
smtp_server = "127.0.0.1"
smtp_port = 1025
smtp_email = "test@test.com"
smtp_password = ""
sender_email = "test@test.com"
receiver_email = ["test1@test.com","test2@test.com"]

#### Mail Subjects & Content ####

sme_SHUT_SUB = "Wildfly Down"
sme_SHUT_CON = "Wildfly is down for maintenance. Your patience is appreciated"

sme_START_SUB = "NNTO : Wildfly Started Successfully"
sme_START_CON = "Wildfly Started Successfully"

sme_RESTART_SUB = "Wildfly Restart"
sme_RESTART_CON = "Wildfly is under restarting. Please wait."


## Autocreated Directories ##

wildfly_bin_dir = wildfly_dir+"bin\\"
standalone_dir = wildfly_dir+"standalone\\"
deploy_dir = standalone_dir+"deployments\\"
server_log_dir = standalone_dir+"log\\"

cmd_standalone="standalone.bat"
cmd_jboss="jboss-cli.bat"

import os
import time
import shutil
import subprocess
import time
from datetime import datetime
import csv
from tkinter import *
import threading
import smtplib, ssl
import email.utils
from email.mime.text import MIMEText
import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
else:

    def port_status():
        tmp = os.popen("netstat -an | findstr 9990 | findstr LISTEN").read()
        if len(tmp)>0:
            return True
        return False
    
    def application_status():
        tmp = subprocess.Popen(wildfly_bin_dir+"jboss-cli.bat --connect command=':read-attribute(name=server-state)'", bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        while tmp.poll() is None:
            line = tmp.stdout.readline()
            line = str(line)
            if 'failed' in line:
                return False
            if 'running' in line:
                return True
            if 'not a valid operation' in line:
                return True
            if 'Press any key to continue' in line:
                tmp.communicate('\r\n')
        return False
    
    def get_user():
        return os.getlogin()
    
    def get_user_name():
        tmp = os.popen('net user {0} /domain | findstr "Full Name"'.format(get_user())).read()
        tmp = tmp.replace("Full Name","")
        name = tmp.split()
        fname = ""
        if len(name) >0:
            fname = name[0]
        return fname
    
    def get_currenttime():
        return time.strftime('%d/%m/%Y %H:%M:%S')
    
    def get_date_diff(past, current):
        return past-current
    
    def wait():
        pass
    
    def set_started():
        user = get_user()
        fname = get_user_name()
        datetime = get_currenttime()
        data = {'user' : user+'('+fname+')',
                'datetime': str(datetime)}
        with open(wildfly_bin_dir+'userinfo.csv', 'w') as f:
            w = csv.DictWriter(f, data.keys())
            w.writerow(dict((fn,fn) for fn in data.keys()))
            w.writerow(data)
        
    def get_started():
        data = {}
        with open(wildfly_bin_dir+'userinfo.csv', 'r') as f:
            r = csv.DictReader(f)
            data = next(r)
            data = dict(data)
        return data
    
    def create_dir(target_folder):
        if os.system("mkdir {0}".format(target_folder))>0:
            out_text = "error creating backup directory. please check configuration.\n"
            update_output(out_text)
            output.update()
            return False
        else:
            out_text = "backup folder created at : {0}\n".format(target_folder)
            update_output(out_text)
            return True
    
    def copy_file(file, src_dir, dest_dir):
        srcfile = os.path.join(src_dir,file)
        out_text = srcfile
        update_output('\n'+out_text)
        destfile = os.path.join(dest_dir,file)
        try: 
            shutil.copyfile(srcfile, destfile)
            return True
        except shutil.SameFileError:        
            out_text = "\nSource and destination represents the same file.\n"
            update_output(out_text)
            return False
        except PermissionError:        
            out_text = "\nPermission denied.\n"
            update_output(out_text)
            return False
        except:        
            out_text = "\nserver log files not found.\n"
            update_output(out_text)
            return True
    
    def backup():
        if port_status():        
            out_text = "Wildfly already running. Please stop the server for backup.\n"
            update_output(out_text)
            return False
        target_folder=backup_dir+time.strftime('%Y-%m-%d-%H_%M_%S')
        if create_dir(target_folder):
            out_text = "copying logfiles..\n"
            update_output(out_text)
            app = True
            server = True
            rlog = True
            file_list = os.listdir(app_log_dir)
            for file in file_list:
                if not copy_file(file,app_log_dir,target_folder):                
                    out_text = "error copying app log files..\n"
                    update_output(out_text)
                    #return False
                else:
                    app = True
            if not copy_file("server.log",server_log_dir,target_folder):            
                out_text = "error copying server log file..\n"
                update_output(out_text)
                return False
            else:
                server = True
            if not copy_file("Rlog.txt",python_log_dir,target_folder):            
                out_text = "error copying python log file..\n"
                update_output(out_text)
                return False
            else:
                rlog = True
    #        if app and server and rlog:            
    #            out_text = "copying war files..\n"          
    #            update_output(out_text)
    #            file_list = os.listdir(deploy_dir)
    #            for file in file_list:
    #                if file.endswith(".war"):          # for testing purpose given '.deployed'. remove '.deployed' for production.
    #                    if not copy_file(str(file),deploy_dir,target_folder):                        
    #                        out_text = "error copying war files..\n"
    #                        update_output(out_text)
    #                        return False
    #        else:            
    #            out_text = "error copying log files\n"
    #            update_output(out_text)
    #            return False
            return True
        else:
            return False
    
    def send_email(opt):
        
        if opt == "start":
            sub = sme_START_SUB
            message = sme_START_CON
        elif opt == "stop":
            sub = sme_SHUT_SUB
            message = sme_SHUT_CON
        elif opt == "restart":
            sub = sme_RESTART_SUB
            message = sme_RESTART_CON
        
        msg = MIMEText(message)
        msg['To'] = email.utils.formataddr(('Recipient', ", ".join(receiver_email)))
        msg['From'] = email.utils.formataddr(('Author', sender_email))
        msg['Subject'] = sub
    
        server = smtplib.SMTP('127.0.0.1', 1025)
    #    server.set_debuglevel(True) # show communication with the server
        try:
            server.sendmail(sender_email, receiver_email, msg.as_string())
    
        except SMTPRecipientsRefused:
            out_text = "mail recepient error\n mail sending failed"
            update_output(out_text)
            server.quit()
            return False
        except SMTPHeloError:
            out_text = "smtp error\n mail sending failed"
            update_output(out_text)        
            return False
        except SMTPSenderRefused:
            out_text = "mail sender error\n mail sending failed"
            update_output(out_text)        
            return False
        except SMTPDataError:
            out_text = "unexpected mailing error\n mail sending failed"
            update_output(out_text)        
            return False        
        finally:
            server.quit()
            out_text = "notification mail sent"
            update_output(out_text)
            return True
    is_deploying_status = False
    def is_deploying():
        global is_deploying_status
        while not is_deploying_status:
            file_list = os.listdir(deploy_dir)
            for file in file_list:
                if file.endswith(".isdeploying"):
                    is_deploying_status = True
        return is_deploying_status
    
    
    partial_status = -5
    def check_partial():
        global partial_status
        
        partial_status = -5
        fail_count = 0
        success_count = 0
        is_deploying_count = 0
        file_list = os.listdir(deploy_dir)
        for file in file_list:
            if file.endswith(".failed"):
                fail_count = fail_count + 1
                break
            elif file.endswith(".deployed"):
                success_count = success_count + 1
        if fail_count > 0:
            if success_count > 0:
                partial_status = 0
            else:
                partial_status = -1
        elif success_count>0:
            partial_status = 1
    
    def check_port_status():
        if not port_status():
            root.after(100,check_port_status)
        updateStatusColor(canvas_port, "green")
        return True
        
    def start_server():
        global partial_status
        global is_deploying_status
        
        set_started()
        props_attr = "-Dprops.path="+props_dir
        time_out_attr = "-Djboss.as.management.blocking.timeout=90000"
        connect_attr = "-b 0.0.0.0"
        subprocess.Popen(' {4}{0} {1} {2} {3}'.format(cmd_standalone, props_attr, time_out_attr, connect_attr, wildfly_bin_dir),shell=True)    
        out_text = "please wait.. we are working on starting the server\n"
        update_output(out_text)
        check_port_status()
        t = threading.Thread(target=is_deploying)
        t.start()
        t.join()
        while not is_deploying_status:
            root.update()
        is_deploying_status = False
        out_text = "deployment started..\n"
        update_output(out_text)
        
        while partial_status == -5:
            check_partial()
            root.update()
        '''
        if partial_status == 0:
            out_text = "\nWildfly started partially\n"
            update_output(out_text)
            updateStatusColor(canvas_app, "yellow")
        elif partial_status == 1:
            out_text = "\nWildfly started successfully\n"
            update_output(out_text)
            updateStatusColor(canvas_app, "green")
        else:
            out_text = "\nWildfly failed to start\n"
            update_output(out_text)
            updateStatusColor(canvas_app, "red")
        '''
        out_text = "\nWildfly started successfully\n"    
        update_output(out_text)
        updateStatusColor(canvas_app, "green")
        partial_status = -5
        button_start.config(text="Restart")
        start_data = get_started()
        set_text(lbl_start_by_val, start_data['user'])
        set_text(lbl_start_date_val, start_data['datetime'])
    
    def shutdown_server():
        out_text = "\nstopping wildfly server.."
        update_output(out_text)
        tmp = subprocess.Popen(wildfly_bin_dir+"jboss-cli.bat --connect controller={0} --command=:shutdown < nul".format(ip))
        while tmp.poll() is None:
            tmp.communicate('\r\n')
        if not port_status() and not application_status():
            updateStatusColor(canvas_port, "red")
            updateStatusColor(canvas_app, "red")    
            return True
        else:
            return False
    
    def delete_directory(path):
        try:
            shutil.rmtree(path)
            return True
        except (FileNotFoundError):        
            out_text = "{0} not found\n".format(path)
            
            return True    
    
    def delete_file(path):
        if os.path.exists(path):
          os.remove(path)
        else:
          print("{0} not found".format(path))
        return True
    
    def delete_temp():    
        out_text = "\ndeleting temporary files..\n"
        update_output(out_text)
        try:
            delete_directory(os.path.join(standalone_dir, 'tmp'))
            delete_directory(os.path.join(standalone_dir, 'data'))
            delete_directory(os.path.join(standalone_dir, 'log'))
    
            file_list = os.listdir(app_log_dir)
            for file in file_list: 
                delete_file(os.path.join(app_log_dir, file))
            
            file_list = os.listdir(deploy_dir)
            for file in file_list:
                if not file.endswith(".war") and not file.endswith(".txt"):        
                    delete_file(os.path.join(deploy_dir, file))
            return True
        except (FileNotFoundError):        
            out_text = "files not found\n"
            update_output(out_text)
            return True
        except PermissionError:        
            out_text = "\nPermission denied while deleting files.\n"
            update_output(out_text)
            return False    
    
    #####   Wildfly GUI    ##### 
    
    
    #*********** GUI Controls ***********#
    
    def buttonStart():
        button_start.config(state="disabled")
        button_stop.config(state="disabled")
        if port_status():
            t = threading.Thread(target=send_email, args=["restart"])
            t.start()
            if shutdown_server():
                out_text = "\nWildfly stopped successfully"
                update_output(out_text)           
        else:
            t = threading.Thread(target=send_email, args=["start"])
            t.start()
        if backup():          
            out_text = "backup successful\n"
            update_output(out_text)
            if delete_temp():                
                out_text = "removed successfully\n\n"
                update_output(out_text)
            else:                
                out_text = "error removing files"
                update_output(out_text)
                out_text = "\nStarting Wildfly \n"
                update_output(out_text)
                start_server()        
            out_text = "Starting Wildfly \n"
            update_output(out_text)
            start_server()
        else:            
            out_text = "backup failed."
            update_output(out_text)
        button_start.config(state="normal")
        button_stop.config(state="normal")
        return True
    
    def buttonStop():
        button_stop.config(state="disabled")
        button_start.config(state="disabled")
        if port_status():
            if shutdown_server():
                out_text = "\nWildfly stopped."
                update_output(out_text)
                button_start.config(text="Start")
                t = threading.Thread(target=send_email, args=["stop"])
                t.start()
        else:
            out_text = "\nUnable to stop the server. Please check the server status"
            update_output(out_text)
        button_stop.config(state="normal")
        button_start.config(state="normal")    
        return True
    
    def buttonRestart():
        if port_status():
            if shutdown_server():
                out_text = "Wildfly stopped successfully"
                update_output(out_text)
            else:
                out_text = "Wildfly was not running.."
                update_output(out_text)
            if backup():
                out_text = "backup successful"
                update_output(out_text)
                if delete_temp():
                    out_text = "removed successfully"
                    update_output(out_text)
                else:
                    out_text = "error removing files"
                    update_output(out_text)
                out_text = "Starting Wildfly \n"
                update_output(out_text)
                start_server()
            else:
                out_text = "backup failed."
                update_output(out_text)
        return True
    
    
    def buttonBackup():
        if backup():
            out_text = "backup successful"
            update_output(out_text)
        else:
            out_text = "backup failed. please see the logs"
            update_output(out_text)
        return True
    
    def buttonClear():
        output.delete(0,END)
        return True
    
    def buttonExit():
        exit(0)
        return True
    
    def update_output(text):
        output.insert(END,text)
        output.see(END)
        root.update_idletasks()
        
    def updateStatusColor(obj, color):
        obj.configure(bg=color)
    
    def set_text(obj, txt):
        obj.config(text=txt)
        
    
    #******* GUI Model********#
    
    root = Tk()
    root.geometry("500x400")
    root.title("Wildfly")
    
    outtext = StringVar()
    outtext.set('Wildfly Console\n')
    
    ##### Wildfly Logo #####
    #Top Frame 
    frame_logo = Frame(root, width = 500, height=100, relief=SUNKEN)
    frame_logo.pack(side=TOP)
    frame_logo.pack_propagate(0)
    lbl_logo = Label(frame_logo, font=('aria',30,'bold' ),text="Wildfly", fg="white", bg="#0d3c65")
    lbl_logo.grid(row=0,column=0)
    lbl_logo.pack(fill=BOTH, expand=1)
    
    
    #Server Status Frame
    frame_status = Frame(root, bg="white", width = 500, height=50, relief=SUNKEN)
    frame_status.pack(padx=20, pady=4, side=TOP, fill='both')
    frame_status.pack_propagate(0)
    
    lbl_port_status = Label(frame_status, font=('aria',10,'bold' ), text="Port Status :  ", fg="black", bg="white")
    lbl_port_status.grid(row=0,column=0)
    canvas_port = Canvas(frame_status, bg = "red", height=25, width=50)
    canvas_port.grid(row=0,column=1)
    
    lbl_app_status = Label(frame_status, font=('aria',10,'bold' ), text="\t\tApplication Status :  ", fg="black", bg="white")
    lbl_app_status.grid(row=0,column=2)
    canvas_app = Canvas(frame_status, bg = "red", height=25, width=50)
    canvas_app.grid(row=0,column=3)
    
    frame_status2 = Frame(root,bg="white",width = 500,height=100,relief=SUNKEN)
    frame_status2.pack(padx=20, pady=4, side=TOP, fill='both')
    frame_status2.pack_propagate(0)
    
    lbl_start_by = Label(frame_status2, font=('aria',10,'bold' ), text="Started By :  ", fg="black", bg="white")
    lbl_start_by.grid(row=0,column=0, sticky=W+E)
    lbl_start_by_val = Label(frame_status2, font=('aria',10,'bold' ), text="", fg="black", bg="white")
    lbl_start_by_val.grid(row=0,column=1, sticky=W+E)
    
    lbl_start_date = Label(frame_status2, font=('aria',10,'bold' ), text="Started Date:  ", fg="black", bg="white")
    lbl_start_date.grid(row=0,column=2, sticky=W+E)
    lbl_start_date_val = Label(frame_status2, font=('aria',10,'bold' ), text="", fg="black", bg="white")
    lbl_start_date_val.grid(row=0,column=3, sticky=W+E)
    
    
    frame_menu = Frame(root,bg="white",width = 500,height=300,relief=SUNKEN)
    frame_menu.pack(padx=20, pady=20, side=TOP)
    frame_menu.pack_propagate(0)
    
    button_start = Button(frame_menu, text="Start", height=2, width=20, command = buttonStart)
    button_start.pack(padx=10, pady=10)
    button_start.grid(row=0,column=0)
    
    
    button_stop = Button(frame_menu, text ="Stop", height=2, width=20, command = buttonStop) 
    button_stop.pack(padx=10, pady=10)
    button_stop.grid(row=0,column=1)
    
    #button_stop = Button(frame_menu, text ="Restart", height=2, width=20, command = buttonRestart) 
    #button_stop.pack(padx=5, pady=5)
    #button_stop.grid(row=1,column=0)
    
    #button_backup = Button(frame_menu, text="Backup", height=2, width=20, command = buttonBackup)
    #button_backup.pack(padx=5, pady=5)
    #button_backup.grid(row=1,column=1)
    
    
    button_clear = Button(frame_menu, text="Clear Console", height=2, width=20, command = buttonClear)
    button_clear.pack(padx=(100, 10), pady=10)
    button_clear.grid(row=1,column=0)
    
    button_clear = Button(frame_menu, text="Exit", height=2, width=20, command = buttonExit)
    button_clear.pack(padx=(100, 10), pady=10)
    button_clear.grid(row=1,column=1)
    
    
    frame_status_bar = Frame(root,bg="black",width = 500,height=100,relief=SUNKEN)
    frame_status_bar.pack(padx=5, pady=5, side=BOTTOM)
    frame_status_bar.pack_propagate(0)
    
    scroll = Scrollbar(frame_status_bar)
    scroll.pack(side = RIGHT, fill = Y)
    
    output = Listbox(frame_status_bar, width="500", height="100", fg="white", bg="black")
    output.insert(END, "Wildfly Console")
    output.pack(expand=True, fill='both')
    
    scroll.config(command=output.yview)
    
    
    ######################################
    ############# GUI Init ###############
    if port_status():
        updateStatusColor(canvas_port, "green")
        start_data = get_started()
        set_text(lbl_start_by_val, start_data['user'])
        set_text(lbl_start_date_val, start_data['datetime'])
        button_start.config(text="Restart")
    else:
        set_text(lbl_start_by_val, 'NA')
        set_text(lbl_start_date_val, 'NA')    
    if application_status(): #remove not
        updateStatusColor(canvas_app, "green")
    
    ### mainloop  ###
    mainloop()
