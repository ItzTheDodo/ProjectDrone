from tkinter import *
from PIL import ImageTk
from ProjectDrone.utils.ProjectUtils import *
from ProjectDrone.DroneAssets.DroneConfiguration import DroneCnf, DroneConfiguration
from ProjectDrone.utils.MapUtils import *
from ProjectDrone.utils.FlightConfigurationFPFile import *
import math
import datetime
from _thread import *


class Client:

    def __init__(self, VERSION, runtime):

        __metadata__ = ReadOnly

        self.VERSION = VERSION
        self.RUNTIME = runtime

        self.BODYFONT = ("Times", 25, 'bold')
        self.HEADERFONT = ("Times", 50, 'bold', 'underline')
        self.BODYFONTU = ("Times", 25, 'bold', 'underline')
        self.SMALLFONT = ("Times", 15, 'bold')
        self.SMALLFONTU = ("Times", 15, 'bold', 'underline')
        self.XSMALLFONT = ("Times", 10, 'bold')

        self.root = Tk()
        self._background_image = PhotoImage(file=os.path.join(self.RUNTIME.DATAFOLDER.getImgItemsFolder(), "bgimg.gif"))
        self.WIDTH = self._background_image.width()
        self.HEIGHT = self._background_image.height()
        self.root.title("Project Drone v%s" % self.VERSION)
        self.root.geometry("%sx%s+50+30" % (self.WIDTH, self.HEIGHT))
        self.root.resizable(0, 0)
        self.cv = Canvas(self.root, width=int(self.WIDTH), height=int(self.HEIGHT))
        self.cv.pack(side='top', fill='both', expand='yes')
        self.cv.create_image(0, 0, image=self._background_image, anchor="nw")

        self.cur_drone_sec = 0
        self.cur_map = None
        self.cur_map_object = None
        self._cur_map_tk = None

        self.unsaved_fplan_locs_xy = []
        self.cur_fplan_pos1 = None
        self.centering = True

        self.map_fpv_toggle = False
        self.cur_stored_file = None
        self.cur_fplan_dist_m = []
        self.land_takeoff_fplango = "Takeoff"
        self.is_in_air = False

        self._init_photos()
        self._draw_navbar()
        self._draw_drone_sel()

        self.root.protocol("WM_DELETE_WINDOW", self.RUNTIME.close)
        self.root.mainloop()

    def _create_drone_profile(self, name, battery, a_s, a_f, img=None):
        profile = DroneConfiguration(name, battery, a_f, a_s, img)
        DroneCnf.append(profile)
        self.RUNTIME.DATAFOLDER.getConfig().setValue("Drone-Configurations.%s" % name, {})
        self.RUNTIME.DATAFOLDER.getConfig().setValue("Drone-Configurations.%s.Battery" % name, str(battery))
        self.RUNTIME.DATAFOLDER.getConfig().setValue("Drone-Configurations.%s.avg-speed" % name, str(a_s))
        self.RUNTIME.DATAFOLDER.getConfig().setValue("Drone-Configurations.%s.avg-flight-time" % name, str(a_f))
        if img is not None:
            self.RUNTIME.DATAFOLDER.getConfig().setValue("Drone-Configurations.%s.image" % name, str(img))
        self.cv.delete("all")
        self.cv.create_image(0, 0, image=self._background_image, anchor="nw")
        self._draw_drone_sel()
        self._draw_navbar()

    def _draw_navbar(self):
        self.cv.create_rectangle(0, 0, 250, self.HEIGHT, fill="#444444", tag="nav_bar")

        self.cv.create_text(25, 10, text="Project Drone", fill="grey", anchor="nw", font=self.BODYFONT, tag="nav_bar")

        cur_drone_cnf = DroneCnf[self.cur_drone_sec]

        self.cv.create_text(25, 150, text="Battery: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="nav_bar")
        en1_plh = StringVar()
        en1 = Entry(self.root, textvariable=en1_plh, width=7)
        en1_plh.set(cur_drone_cnf.getBattery())
        self.cv.create_window(110, 153, window=en1, anchor="nw")

        self.cv.create_text(25, 200, text="Average Speed: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="nav_bar")
        en2_plh = StringVar()
        en2 = Entry(self.root, textvariable=en2_plh, width=7)
        en2_plh.set(cur_drone_cnf.getAverageSpeed())
        self.cv.create_window(170, 203, window=en2, anchor="nw")

        self.cv.create_text(15, 250, text="Average Flight Time: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="nav_bar")
        en3_plh = StringVar()
        en3 = Entry(self.root, textvariable=en3_plh, width=7)
        en3_plh.set(cur_drone_cnf.getAverageFlightTime())
        self.cv.create_window(200, 253, window=en3, anchor="nw")

        b = Button(self.root, text="Start Flight", command=self._open_flight_screen, width=18, font=self.SMALLFONT, borderwidth=2, height=1, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(15, self.HEIGHT - 50, window=b, anchor="nw", tag="nav_bar")

        b1 = Button(self.root, text="Create Flight Plan", command=self._open_cr_flight_plan_screen, width=18, font=self.SMALLFONT, borderwidth=2, height=1, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(15, self.HEIGHT - 100, window=b1, anchor="nw", tag="nav_bar")

        b2 = Button(self.root, text="Create Drone Profile", command=lambda: self._create_drone_profile_screen(False, False, "", "", "", "", ""), width=15, font=self.SMALLFONT, borderwidth=2, height=1, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(750, self.HEIGHT - 50, window=b2, anchor="nw", tag="nav_bar")

    def _init_photos(self):
        self.drone_imgs = {}
        self.other_imgs = {}
        for i in os.listdir(self.RUNTIME.DATAFOLDER.getImgItemsFolder()):
            cur_img = os.path.join(self.RUNTIME.DATAFOLDER.getImgItemsFolder(), i)
            if os.path.isfile(cur_img) and i.__contains__("_drone"):
                self.drone_imgs[i] = PhotoImage(file=cur_img)
            else:
                self.other_imgs[i] = PhotoImage(file=cur_img)

    def _move_drone_right_select(self):
        if len(DroneCnf) - 1 == self.cur_drone_sec:
            self.cur_drone_sec = 0
        else:
            self.cur_drone_sec += 1
        self.cv.delete("drone_select")
        self.cv.delete("nav_bar")
        self._draw_drone_sel()
        self._draw_navbar()

    def _move_drone_left_select(self):
        if 0 == self.cur_drone_sec:
            self.cur_drone_sec = len(DroneCnf) - 1
        else:
            self.cur_drone_sec -= 1
        self.cv.delete("drone_select")
        self.cv.delete("nav_bar")
        self._draw_drone_sel()
        self._draw_navbar()

    def _draw_drone_sel(self):

        cur_drone_cnf = DroneCnf[self.cur_drone_sec]

        self.cv.create_text(410, 30, text=cur_drone_cnf.getName(), fill="black", anchor="nw", font=self.HEADERFONT, tag="drone_select")
        b = Button(self.root, text="<", command=self._move_drone_left_select, width=3, font=self.BODYFONT, borderwidth=0, height=1, background="#ffffff", cursor="hand2", activebackground="#ffffff", fg="black")
        b1 = Button(self.root, text=">", command=self._move_drone_right_select, width=3, font=self.BODYFONT, borderwidth=0, height=1, background="#ffffff", cursor="hand2", activebackground="#ffffff", fg="black")
        self.cv.create_window(300, 230, window=b, anchor="nw", tag="drone_select")
        self.cv.create_window(850, 230, window=b1, anchor="nw", tag="drone_select")

        if not cur_drone_cnf.getImg():
            self.cv.create_image(300, 50, image=self.drone_imgs["blank_drone.gif"], anchor="nw", tag="drone_select")
        else:
            try:
                self.cv.create_image(300, 50, image=self.drone_imgs[cur_drone_cnf.getImg().split("\\")[len(cur_drone_cnf.getImg().split("\\")) - 1]], anchor="nw", tag="drone_select")
            except KeyError:
                self.cv.create_image(300, 50, image=self.other_imgs[cur_drone_cnf.getImg().split("\\")[len(cur_drone_cnf.getImg().split("\\")) - 1]], anchor="nw", tag="drone_select")

    def _create_drone_profile_screen(self, is_inv_img, is_inv_txt, cur_img, *cnf_txt):
        self.cv.delete("all")
        self.cv.create_image(0, 0, image=self._background_image, anchor="nw")

        self.cv.create_rectangle(0, 0, 250, self.HEIGHT, fill="#444444")
        self.cv.create_text(25, 10, text="Project Drone", fill="grey", anchor="nw", font=self.BODYFONT)

        if cur_img is None or cur_img == "":
            self.cv.create_image(300, 50, image=self.drone_imgs["blank_drone.gif"], anchor="nw", tag="pl_hold_cr_dr_sc")
        else:
            try:
                self.cv.create_image(300, 50, image=self.drone_imgs[cur_img.split("\\")[len(cur_img.split("\\")) - 1]], anchor="nw", tag="pl_hold_cr_dr_sc")
            except KeyError:
                try:
                    self.cv.create_image(300, 50, image=self.other_imgs[cur_img.split("\\")[len(cur_img.split("\\")) - 1]], anchor="nw", tag="pl_hold_cr_dr_sc")
                except KeyError:
                    self.cv.create_image(300, 50, image=self.drone_imgs["blank_drone.gif"], anchor="nw", tag="pl_hold_cr_dr_sc")

        if self.centering:
            self.cv.create_image(300, 50, image=self.other_imgs["centering_img.gif"], anchor="nw", tag="pl_hold_cr_dr_sc")

        self.cv.create_text(25, 100, text="Name: ", fill="grey", anchor="nw", font=self.SMALLFONT)
        en0_plh = StringVar()
        en0 = Entry(self.root, textvariable=en0_plh, width=10)
        en0_plh.set(cnf_txt[0])
        self.cv.create_window(100, 103, window=en0, anchor="nw")

        self.cv.create_text(25, 150, text="Battery: ", fill="grey", anchor="nw", font=self.SMALLFONT)
        en1_plh = StringVar()
        en1 = Entry(self.root, textvariable=en1_plh, width=7)
        en1_plh.set(cnf_txt[1])
        self.cv.create_window(110, 153, window=en1, anchor="nw")

        self.cv.create_text(25, 200, text="Average Speed: ", fill="grey", anchor="nw", font=self.SMALLFONT)
        en2_plh = StringVar()
        en2 = Entry(self.root, textvariable=en2_plh, width=7)
        en2_plh.set(cnf_txt[2])
        self.cv.create_window(170, 203, window=en2, anchor="nw")

        self.cv.create_text(15, 250, text="Average Flight Time: ", fill="grey", anchor="nw", font=self.SMALLFONT)
        en3_plh = StringVar()
        en3 = Entry(self.root, textvariable=en3_plh, width=7)
        en3_plh.set(cnf_txt[3])
        self.cv.create_window(200, 253, window=en3, anchor="nw")

        self.cv.create_text(25, 300, text="Image (path): ", fill="grey", anchor="nw", font=self.SMALLFONT)
        en4_plh = StringVar()
        en4 = Entry(self.root, textvariable=en4_plh, width=15)
        en4_plh.set(cur_img)
        self.cv.create_window(150, 303, window=en4, anchor="nw")
        if is_inv_img:
            self.cv.create_text(150, 330, text="Invalid Path!", fill="grey", anchor="nw", font=self.XSMALLFONT)

        if is_inv_txt:
            self.cv.create_text(60, 375, text="Invalid Values!", fill="grey", anchor="nw", font=self.SMALLFONT)

        b = Button(self.root, text="<", command=self._open_main_screen, width=3, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(10, 453, window=b, anchor="nw")

        b1 = Button(self.root, text="Create Profile", command=lambda: self._validate_profile(en0, en1, en2, en3, en4), width=12, font=self.SMALLFONT, borderwidth=2, height=2, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(90, self.HEIGHT - 80, window=b1, anchor="nw", tag="nav_bar")

        b2 = Button(self.root, text="Preview Image", command=lambda: self._open_img_drone_prcr_sc(en4, en0, en1, en2, en3), width=18, font=self.SMALLFONT, borderwidth=2, height=1, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(15, self.HEIGHT - 130, window=b2, anchor="nw", tag="nav_bar")

        b3 = Button(self.root, text="Toggle Centering", command=lambda: self._toggle_centering(is_inv_img, is_inv_txt, en0, en1, en2, en3, en4), width=18, font=self.SMALLFONT, borderwidth=2, height=1, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(500, self.HEIGHT - 50, window=b3, anchor="nw", tag="nav_bar")

    def _toggle_centering(self, is_inv_img, is_inv_txt, *cnf_txt):
        self.centering = not self.centering
        out = []
        for i in cnf_txt:
            out.append(i.get())
        self._create_drone_profile_screen(is_inv_img, is_inv_txt, out[len(out) - 1], *out)

    def _validate_profile(self, *cnf):
        out = []
        for i in cnf:
            out.append(i.get())
        count = 0
        for i in cnf:
            if 0 < count < 4:
                try:
                    int(i.get())
                except ValueError:
                    self._create_drone_profile_screen(False, True, out[len(out) - 1], *out[:len(out) - 1])
                    return
            count += 1
        if out[4] == "" or out[4] is None:
            self._create_drone_profile(out[0], out[1], out[2], out[3])
        else:
            self._create_drone_profile(out[0], out[1], out[2], out[3], out[4])

    def _open_img_drone_prcr_sc(self, cur_path, *cnf):
        if cur_path.get() is not None and not cur_path.get() == "" and not cur_path.get() == " ":
            try:
                self.drone_imgs[cur_path.get().split("\\")[len(cur_path.get().split("\\")) - 1]] = PhotoImage(file=cur_path.get())
            except TclError:
                out = []
                for i in cnf:
                    out.append(i.get())
                self._create_drone_profile_screen(True, False, "", *out)
                return
            except KeyError:
                self.other_imgs[cur_path.get().split("\\")[len(cur_path.get().split("\\")) - 1]] = PhotoImage(file=cur_path.get())
        out = []
        for i in cnf:
            out.append(i.get())
        self._create_drone_profile_screen(False, False, cur_path.get(), *out)

    def _open_main_screen(self):
        self.cv.delete("all")
        self._unbind_fplan_keys()
        self.unsaved_fplan_locs_xy = []
        self.cur_fplan_pos1 = None
        self.cv.create_image(0, 0, image=self._background_image, anchor="nw")
        self._draw_drone_sel()
        self._draw_navbar()

    def _open_cr_flight_plan_screen(self, i=False):
        self.cv.delete("all")
        self.root.bind_all("<Escape>", self._exit_undo_fplan_cnf)
        self.root.bind_all("<Button-1>", self._create_line_fplan)
        if self.cur_map is None:
            cur_location = get_current_client_location_latlng()
            self.cur_map_object = MapGen(self.RUNTIME, cur_location[1], cur_location[0], self.WIDTH, self.HEIGHT)
            self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._cur_map_tk = ImageTk.PhotoImage(self.cur_map)
        self.cv.create_image(250, 0, image=self._cur_map_tk, anchor="nw", tag="map")

        self._draw_flight_plan_nav_bar(i, "", "", "")
        self._draw_zoom_buttons()

    def _create_line_fplan(self, e=None):
        if self.cur_fplan_pos1 is None:
            self.root.bind_all("<Motion>", self._update_line_fplan)
            self.cur_fplan_pos1 = [e.x, e.y]
        else:
            self.root.unbind_all("<Motion>")
            cur_loc = len(self.unsaved_fplan_locs_xy)
            self.unsaved_fplan_locs_xy.append([self.cur_fplan_pos1, [e.x, e.y]])
            self.cv.delete("fplan_line")
            self.cv.create_line(self.cur_fplan_pos1[0], self.cur_fplan_pos1[1], e.x, e.y, width=2, tag="saved_fplan_line_%s" % str(cur_loc))
            self.cur_fplan_pos1 = None
            self._update_fplan_log()

    def _update_line_fplan(self, e=None):
        self.cv.delete("fplan_line")
        if e.x < 250:
            self._exit_undo_fplan_cnf()
            return
        self.cv.create_line(self.cur_fplan_pos1[0], self.cur_fplan_pos1[1], e.x, e.y, width=2, tag="fplan_line")

    def _exit_undo_fplan_cnf(self, e=None):
        if self.cur_fplan_pos1 is None:
            cur_loc = len(self.unsaved_fplan_locs_xy) - 1
            if cur_loc == -1:
                return
            self.unsaved_fplan_locs_xy.pop(cur_loc)
            self.cv.delete("saved_fplan_line_%s" % str(cur_loc))
            self._update_fplan_log()
        else:
            self.cv.delete("fplan_line")
            self.root.unbind_all("<Motion>")
            self.cur_fplan_pos1 = None

    def _update_fplan_log(self):
        self.cv.delete("fplan_log")
        count = 0
        for i in self.unsaved_fplan_locs_xy:
            self.cv.create_text(15, 250 + (20 * count), text="%s: %s" % (str(count), str(i)), fill="grey", anchor="nw", font=self.XSMALLFONT, tag="fplan_log")
            count += 1

    def _draw_flight_plan_nav_bar(self, err=False, *cnf):
        self.cv.create_rectangle(0, 0, 250, self.HEIGHT, fill="#444444", tag="flight_plan_cr_nav_bar")
        self.cv.create_text(25, 10, text="Project Drone", fill="grey", anchor="nw", font=self.BODYFONT, tag="flight_plan_cr_nav_bar")

        self.cv.create_text(25, 70, text="Lat: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="flight_plan_cr_nav_bar")
        en0_plh = StringVar()
        en0 = Entry(self.root, textvariable=en0_plh, width=10)
        en0_plh.set(cnf[0])
        self.cv.create_window(100, 73, window=en0, anchor="nw", tag="flight_plan_cr_nav_bar")

        self.cv.create_text(25, 120, text="Long: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="flight_plan_cr_nav_bar")
        en1_plh = StringVar()
        en1 = Entry(self.root, textvariable=en1_plh, width=10)
        en1_plh.set(cnf[1])
        self.cv.create_window(100, 123, window=en1, anchor="nw", tag="flight_plan_cr_nav_bar")

        self.cv.create_text(25, 170, text="Name: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="flight_plan_cr_nav_bar")
        en2_plh = StringVar()
        en2 = Entry(self.root, textvariable=en2_plh, width=15)
        en2_plh.set(cnf[2])
        self.cv.create_window(100, 173, window=en2, anchor="nw", tag="flight_plan_cr_nav_bar")

        if err:
            self.cv.create_text(20, 380, text="Invalid Values!", fill="grey", anchor="nw", font=self.XSMALLFONT, tag="flight_plan_cr_nav_bar")

        self.cv.create_text(15, 220, text="Current Flight Plan Cnf: ", fill="grey", anchor="nw", font=self.SMALLFONTU, tag="flight_plan_cr_nav_bar")

        b = Button(self.root, text="<", command=self._open_main_screen, width=3, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(10, 453, window=b, anchor="nw", tag="flight_plan_cr_nav_bar")

        b2 = Button(self.root, text="Update Map", command=lambda: self._redraw_map(en0, en1), width=18, font=self.SMALLFONT, borderwidth=2, height=1, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(15, self.HEIGHT - 130, window=b2, anchor="nw", tag="flight_plan_cr_nav_bar")

        b2 = Button(self.root, text="Create Plan", command=lambda: self._create_fplan_file(en2), width=12, height=2, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(90, 453, window=b2, anchor="nw", tag="flight_plan_cr_nav_bar")

    def _redraw_map(self, lat, long):
        if lat.get() == "" or lat.get() is None or long.get() == "" or long.get() is None:
            return
        self.cur_map_object.setLatitude(lat.get())
        self.cur_map_object.setLongatude(long.get())
        self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._open_cr_flight_plan_screen()

    def _map_zoom_pos(self):
        if self.cur_map_object.getZoom() == 22:
            return
        self.unsaved_fplan_locs_xy = []
        self.cur_fplan_pos1 = None
        self.root.unbind_all("<Motion>")
        self.cur_map_object.setZoom(self.cur_map_object.getZoom() + 1)
        self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._open_cr_flight_plan_screen()

    def _map_zoom_neg(self):
        if self.cur_map_object.getZoom() == 0:
            return
        self.unsaved_fplan_locs_xy = []
        self.cur_fplan_pos1 = None
        self.root.unbind_all("<Motion>")
        self.cur_map_object.setZoom(self.cur_map_object.getZoom() - 1)
        self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._open_cr_flight_plan_screen()

    def _draw_zoom_buttons(self):
        b = Button(self.root, text="+", command=self._map_zoom_pos, width=1, height=1, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(900, 460, window=b, anchor="nw")

        b1 = Button(self.root, text="-", command=self._map_zoom_neg, width=1, height=1, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(900, 390, window=b1, anchor="nw")

    def _unbind_fplan_keys(self):
        self.root.unbind_all("<Escape>")
        self.root.unbind_all("<Button-1>")
        self.root.unbind_all("<Motion>")

    def _create_fplan_file(self, namew):
        geocoords = []
        if len(self.unsaved_fplan_locs_xy) < 2 or namew.get() == "":
            self._open_cr_flight_plan_screen(True)
            return
        for i in self.unsaved_fplan_locs_xy:
            geocoords.append([[i[0][0], i[0][1]], [i[1][0], i[1][1]]])
        fplan = FPFile(self.RUNTIME, namew.get(), [self.cur_map_object.getLatitude(), self.cur_map_object.getLongatude(), self.cur_map_object.getZoom()], geocoords)
        fplan.create()
        self.unsaved_fplan_locs_xy = []
        self.cur_fplan_pos1 = None
        self.root.unbind_all("<Motion>")
        self._open_cr_flight_plan_screen()

    def _open_flight_screen(self):
        self.cv.delete("all")

        if self.cur_map is None:
            cur_location = get_current_client_location_latlng()
            self.cur_map_object = MapGen(self.RUNTIME, cur_location[1], cur_location[0], self.WIDTH, self.HEIGHT)
            self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._cur_map_tk = ImageTk.PhotoImage(self.cur_map)
        self.cv.create_image(0, 60, image=self._cur_map_tk, anchor="nw", tag="flight_bg")

        self._draw_start_flight_screen()

    def _draw_start_flight_screen(self):
        self.cv.create_rectangle(0, 0, self.WIDTH, 60, fill="#444444", tag="start_flight_nav_bar")
        self.cv.create_text(25, 10, text="Project Drone", fill="grey", anchor="nw", font=self.BODYFONT, tag="start_flight_nav_bar")

        self.cv.create_text(290, 20, text="Flight Driver: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="start_flight_nav_bar")
        driver_options = []
        if len(self.RUNTIME.drivers) == 0:
            driver_options.append("No Stored Drivers")
        else:
            for i in self.RUNTIME.drivers:
                driver_options.append(i.split("\\")[len(i.split("\\")) - 1].split(".")[0])

        driver_options_select = StringVar(self.root)
        driver_options_select.set("------- None -------")
        driver_dropdown = OptionMenu(self.root, driver_options_select, *driver_options)
        self.cv.create_window(500, 32, window=driver_dropdown, tag="start_flight_nav_bar")

        self.cv.create_text(620, 20, text="Flight Plan: ", fill="grey", anchor="nw", font=self.SMALLFONT, tag="start_flight_nav_bar")
        options = []
        if len(os.listdir(self.RUNTIME.DATAFOLDER.getFlightPlanFolder())) == 0:
            options.append("No Stored Flight Plans")
        else:
            for i in os.listdir(self.RUNTIME.DATAFOLDER.getFlightPlanFolder()):
                options.append(i.split(".")[0])
            options.append("None")

        fplan_options = StringVar(self.root)
        fplan_options.set("------- None -------")
        fplan_dropdown = OptionMenu(self.root, fplan_options, *options)
        self.cv.create_window(800, 32, window=fplan_dropdown, tag="start_flight_nav_bar")

        b3 = Button(self.root, text="Go", command=lambda: self._use_fplan_load(fplan_options, driver_options_select), width=3, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(890, 14, window=b3, anchor="nw", tag="start_flight_nav_bar")

        if self.map_fpv_toggle:
            b = Button(self.root, text="Map", command=lambda x=driver_options_select: self._drone_map_view(x), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="black")
            self.cv.create_window(760, 480, window=b, anchor="nw", tag="map_fpv_toggle_button")
            b1 = Button(self.root, text="FPV", command=lambda x=driver_options_select: self._drone_fpv_view(x), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
            self.cv.create_window(850, 480, window=b1, anchor="nw", tag="map_fpv_toggle_button")
        else:
            b = Button(self.root, text="Map", command=lambda x=driver_options_select: self._drone_map_view(x), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
            self.cv.create_window(760, 480, window=b, anchor="nw", tag="map_fpv_toggle_button")
            b1 = Button(self.root, text="FPV", command=lambda x=driver_options_select: self._drone_fpv_view(x), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="black")
            self.cv.create_window(850, 480, window=b1, anchor="nw", tag="map_fpv_toggle_button")

        self.land_takeoff_fplango = "Takeoff"
        b4 = Button(self.root, text=self.land_takeoff_fplango, command=lambda x=driver_options_select: self._takeoff_using_driver(x), width=7, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(400, 480, window=b4, anchor="nw", tag="land_takeoff_button")

        b5 = Button(self.root, text="<", command=self._open_main_screen, width=3, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(10, 453, window=b5, anchor="nw", tag="flight_plan_cr_nav_bar")

        self._draw_zoom_buttons_flight()

    def _draw_zoom_buttons_flight(self):
        b4 = Button(self.root, text="+", command=self._flight_map_pos, width=1, height=1, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(15, 370, window=b4, anchor="nw", tag="map_fpv_toggle_button")

        b5 = Button(self.root, text="-", command=self._flight_map_neg, width=1, height=1, font=self.BODYFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(15, 300, window=b5, anchor="nw", tag="map_fpv_toggle_button")

    def _flight_map_pos(self):
        if self.cur_map_object.getZoom() == 22:
            return
        self.cur_map_object.setZoom(self.cur_map_object.getZoom() + 1)
        self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._open_flight_screen()

    def _flight_map_neg(self):
        if self.cur_map_object.getZoom() == 0:
            return
        self.cur_map_object.setZoom(self.cur_map_object.getZoom() - 1)
        self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._open_flight_screen()

    def _drone_map_view(self, d):
        if not self.map_fpv_toggle:
            return

        self.cv.delete("flight_bg")
        self.cv.delete("fplan_show")

        if self.cur_map is None:
            cur_location = get_current_client_location_latlng()
            self.cur_map_object = MapGen(self.RUNTIME, cur_location[1], cur_location[0], self.WIDTH, self.HEIGHT)
            self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._cur_map_tk = ImageTk.PhotoImage(self.cur_map)
        self.cv.create_image(0, 60, image=self._cur_map_tk, anchor="nw", tag="flight_bg")

        self.cv.delete("map_fpv_toggle_button")
        self.map_fpv_toggle = not self.map_fpv_toggle
        b = Button(self.root, text="Map", command=lambda: self._drone_map_view(d), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(760, 480, window=b, anchor="nw", tag="map_fpv_toggle_button")
        b1 = Button(self.root, text="FPV", command=lambda: self._drone_fpv_view(d), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(850, 480, window=b1, anchor="nw", tag="map_fpv_toggle_button")

        self._draw_zoom_buttons_flight()

    def _drone_fpv_view(self, d):
        if self.map_fpv_toggle:
            return

        driver = d.get()

        self.cv.delete("flight_bg")
        self.cv.delete("fplan_show")
        if driver is not None and driver != "------- None -------":
            count = 0
            cur_driver_path = None
            for i in self.RUNTIME.drivers:
                if i.split("\\")[len(i.split("\\")) - 1].split(".")[0] == driver:
                    cur_driver_path = self.RUNTIME.DATAFOLDER.getDriverFolder().driver_imports[count][1]
                count += 1
            if cur_driver_path is None:
                return
            if cur_driver_path.FPV_Enabled():
                self.cv.create_window(0, 60, window=cur_driver_path.FPV_tkWidget(), anchor="nw", tag="flight_bg")

        self.cv.delete("map_fpv_toggle_button")
        self.map_fpv_toggle = not self.map_fpv_toggle
        b = Button(self.root, text="Map", command=lambda: self._drone_map_view(d), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="black")
        self.cv.create_window(760, 480, window=b, anchor="nw", tag="map_fpv_toggle_button")
        b1 = Button(self.root, text="FPV", command=lambda: self._drone_fpv_view(d), width=6, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(850, 480, window=b1, anchor="nw", tag="map_fpv_toggle_button")

    def _use_fplan_load(self, tkdropwidg, d):
        name = tkdropwidg.get()
        if name == "------- None -------" or name == "No Stored Flight Plans" or self.is_in_air:
            return

        if name == "None":
            self.cv.delete("fplan_show")
            self.cv.delete("flight_bg")
            cur_location = get_current_client_location_latlng()
            self.cur_map_object.setLatitude(cur_location[0])
            self.cur_map_object.setLongatude(cur_location[1])
            self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
            self._cur_map_tk = ImageTk.PhotoImage(self.cur_map)
            self.cv.create_image(0, 60, image=self._cur_map_tk, anchor="nw", tag="flight_bg")
            self.cv.delete("land_takeoff_button")
            self.land_takeoff_fplango = "Takeoff"
            b4 = Button(self.root, text=self.land_takeoff_fplango, command=self._takeoff_using_driver, width=7, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
            self.cv.create_window(400, 480, window=b4, anchor="nw", tag="land_takeoff_button")
            return

        self.cur_stored_file = parse_FPFile(os.path.join(self.RUNTIME.DATAFOLDER.getFlightPlanFolder(), name + ".fp"))

        self.cv.delete("fplan_show")
        self.cv.delete("flight_bg")
        self.cv.delete("land_takeoff_button")
        self.cur_map_object.setLatitude(self.cur_stored_file[0][0])
        self.cur_map_object.setLongatude(self.cur_stored_file[0][1])
        self.cur_map_object.setZoom(self.cur_stored_file[0][2])
        self.cur_map = self.cur_map_object.getMap().resize((self.WIDTH, self.HEIGHT))
        self._cur_map_tk = ImageTk.PhotoImage(self.cur_map)
        self.cv.create_image(0, 60, image=self._cur_map_tk, anchor="nw", tag="flight_bg")

        self.land_takeoff_fplango = "Start"
        b4 = Button(self.root, text=self.land_takeoff_fplango, command=lambda: self._start_fplan_flight(d), width=7, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(400, 480, window=b4, anchor="nw", tag="land_takeoff_button")

        self.cur_fplan_dist_m = []
        for i in self.cur_stored_file[1]:
            cur_item = literal_eval(i)
            pos1 = cur_item[0]
            pos2 = cur_item[1]
            mtop = latlongtometersppix(self.cur_map_object.getLatitude(), self.cur_map_object.getZoom())
            self.cur_fplan_dist_m.append(math.sqrt(math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2)) * mtop)
            self.cv.create_line(pos1[0] - 250, pos1[1] + 60, pos2[0] - 250, pos2[1] + 60, width=2, tag="fplan_show")

    def _start_fplan_flight(self, d):
        vs = int(self.RUNTIME.DATAFOLDER.getConfig().getValue("fplan-vs"))
        height = int(self.RUNTIME.DATAFOLDER.getConfig().getValue("fplan-height"))
        rs = int(self.RUNTIME.DATAFOLDER.getConfig().getValue("fplan-rotational-speed-dps"))
        cur_drone_cnf = DroneCnf[self.cur_drone_sec]

        driver = d.get()
        if driver is None or driver == "------- None -------":
            return
        count = 0
        cur_driver = None
        for i in self.RUNTIME.drivers:
            if i.split("\\")[len(i.split("\\")) - 1].split(".")[0] == driver:
                cur_driver = self.RUNTIME.DATAFOLDER.getDriverFolder().driver_imports[count][1]
            count += 1
        if cur_driver is None:
            return

        self.cv.delete("land_takeoff_button")
        self.cv.create_text(380, 480, text="Flight Plan In Progress", fill="black", anchor="nw", font=self.SMALLFONT, tag="land_takeoff_button")
        self.bearing = 0

        cur_driver.takeoff()
        self._for_x_sec(height / vs, cur_driver.up)
        fplan_legs = []
        for i in self.cur_stored_file[1]:
            cur_item = literal_eval(i)
            pos1 = cur_item[0]
            pos2 = cur_item[1]
            fplan_legs.append([pos1, pos2])

        start_new_thread(self._update_sc_drone_pos, (cur_driver,))
        if cur_driver.geoLocationEnabled():
            while True:
                dir = self._calibrate_dir_geoloc(cur_driver)
                fplan_dir = self._get_bearing_xy(fplan_legs[0][0], fplan_legs[0][1])
                self.bearing = dir
                turn = fplan_dir - dir
                if -3 > turn < 3:
                    break
                elif turn < 0:
                    self._for_x_sec(turn / rs, cur_driver.left)
                else:
                    self._for_x_sec(turn / rs, cur_driver.right)
                self.cv.update()
            for i in self.cur_fplan_dist_m:
                self._for_x_sec(int(i) / cur_drone_cnf.getAverageSpeed(), cur_driver.forward)
                while True:
                    dir = self._calibrate_dir_geoloc(cur_driver)
                    fplan_dir = self._get_bearing_xy(i[0], i[1])
                    self.bearing = dir
                    turn = fplan_dir - dir
                    if -3 > turn < 3:
                        break
                    elif turn < 0:
                        self._for_x_sec(turn / rs, cur_driver.left)
                    else:
                        self._for_x_sec(turn / rs, cur_driver.right)
                    self.cv.update()
        else:
            count = 0
            for i in self.cur_fplan_dist_m:
                self._for_x_sec(int(i) / cur_drone_cnf.getAverageSpeed(), cur_driver.forward)
                cur_dir = self._get_bearing_xy(i[0], i[1])
                new_dir = self._get_bearing_xy(self.cur_fplan_dist_m[count][0], self.cur_fplan_dist_m[count][1])
                turn = new_dir - cur_dir
                if -3 > turn < 3:
                    break
                elif turn < 0:
                    self._for_x_sec(turn / rs, cur_driver.left)
                else:
                    self._for_x_sec(turn / rs, cur_driver.right)
                count += 1
        self._for_x_sec(height / vs, cur_driver.down)
        cur_driver.land()

        self.cv.delete("land_takeoff_button")
        self.land_takeoff_fplango = "Start"
        b = Button(self.root, text=self.land_takeoff_fplango, command=lambda: self._start_fplan_flight(d), width=7, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(400, 480, window=b, anchor="nw", tag="land_takeoff_button")

    def _update_sc_drone_pos(self, driver):
        en = driver.geoLocationEnabled()
        last_pass = []
        if en:
            last_pass = driver.getGeoLocation()
        while True:
            if en:
                loc = driver.getGeoLocation()
                mtop = latlongtometersppix(self.cur_map_object.getLatitude(), self.cur_map_object.getZoom())
                dist_travelled_m = self._geocoords_to_m(int(last_pass[0]), int(last_pass[1]), int(loc[0]), int(loc[1]))
                start_dist_from_map_origin = self._geocoords_to_m(int(self.cur_map_object.getLatitude()), int(self.cur_map_object.getLongatude()), int(last_pass[0]), int(last_pass[1]))
                pix_center = self.WIDTH / 2, (self.HEIGHT - 60) / 2
                start_point = pix_center + (start_dist_from_map_origin / mtop)
                dist_travelled_pix = dist_travelled_m / mtop
                dyax = 90 - dist_travelled_pix * math.sin(self.bearing)
                dxax = 90 - dist_travelled_pix * math.cos(self.bearing)
                self.cv.delete("drone_rep")
                self.cv.create_image(dxax + start_point, dyax + start_point, image=self.drone_imgs["blank_dr_rep.gif"], anchor="nw", tag="drone_rep")
                last_pass = loc
            else:
                break

    def _for_x_sec(self, sec, command):
        stop_time = (datetime.datetime.now() + datetime.timedelta(seconds=int(sec))).time().strftime("%H:%M:%S").split(":")
        while True:
            now = datetime.datetime.now().strftime("%H:%M:%S").split(":")
            if int(stop_time[0]) >= int(now[0]) and int(stop_time[1]) >= int(now[1]) and int(stop_time[2]) >= int(now[2]):
                break
            command()
            self.cv.update()

    def _geocoords_to_m(self, lat1, lon1, lat2, lon2):
        # start - new
        r = 6378.137
        dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
        dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) + math.cos(lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = r * c
        return d * 1000

    def _calibrate_dir_geoloc(self, drone):
        coord1 = drone.getGeoLocation()
        self._for_x_sec(1, drone.forward)
        coord2 = drone.getGeoLocation()
        b = self._get_bearing_xy(coord1, coord2)
        self._for_x_sec(1, drone.backward)
        return b

    def _get_bearing_xy(self, c1, c2):
        TWOPI = 6.2831853071795865
        RAD2DEG = 57.2957795130823209
        if c1[0] == c2[0] and c1[1] == c2[1]:
            return 0
        theta = math.atan2(c2[0] - c1[0], c1[1] - c2[1])
        if theta < 0.0:
            theta += TWOPI
        return RAD2DEG * theta

    def _takeoff_using_driver(self, d):
        driver = d.get()
        if driver is None and self.land_takeoff_fplango == "Takeoff" or driver == "------- None -------":
            return
        count = 0
        cur_driver_path = None
        for i in self.RUNTIME.drivers:
            if i.split("\\")[len(i.split("\\")) - 1].split(".")[0] == driver:
                cur_driver_path = self.RUNTIME.DATAFOLDER.getDriverFolder().driver_imports[count][1]
            count += 1
        if cur_driver_path is None:
            return
        start_new_thread(self._update_sc_drone_pos, cur_driver_path)
        cur_driver_path.takeoff()
        self.cv.delete("land_takeoff_button")
        self.land_takeoff_fplango = "Land"
        b4 = Button(self.root, text=self.land_takeoff_fplango, command=lambda: self._land_using_driver(d), width=7, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(400, 480, window=b4, anchor="nw", tag="land_takeoff_button")

    def _land_using_driver(self, d):
        driver = d.get()
        if driver is None and self.land_takeoff_fplango == "Land" or driver == "------- None -------":
            return
        count = 0
        cur_driver_path = None
        for i in self.RUNTIME.drivers:
            if i.split("\\")[len(i.split("\\")) - 1].split(".")[0] == driver:
                cur_driver_path = self.RUNTIME.DATAFOLDER.getDriverFolder().driver_imports[count][1]
            count += 1
        if cur_driver_path is None:
            return
        cur_driver_path.land()
        self.cv.delete("land_takeoff_button")
        self.land_takeoff_fplango = "Takeoff"
        b4 = Button(self.root, text=self.land_takeoff_fplango, command=lambda: self._takeoff_using_driver(d), width=7, height=1, font=self.SMALLFONT, borderwidth=2, background="grey", cursor="hand2", activebackground="grey", fg="white")
        self.cv.create_window(400, 480, window=b4, anchor="nw", tag="land_takeoff_button")

    def _get_drone_loc_using_driver(self, d):
        driver = d.get()
        if driver is None or driver == "------- None -------":
            return
        count = 0
        cur_driver_path = None
        for i in self.RUNTIME.drivers:
            if i.split("\\")[len(i.split("\\")) - 1].split(".")[0] == driver:
                cur_driver_path = self.RUNTIME.DATAFOLDER.getDriverFolder().driver_imports[count][1]
            count += 1
        if cur_driver_path is None:
            return
        return cur_driver_path.getGeoLocation()
