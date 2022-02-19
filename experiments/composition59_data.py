import json
import shutil

yellow = "yellow"
blue = "blue"
green = "green"
red = "red"
orange = "orange"
black = "black"
white = "white"
violet = "violet"
magenta = "neon magenta"
neon_green = "neon green"
neon_yellow = "neon yellow"
neon_orange = "neon orange"

path = (
    "Z:\\Dropbox\\0_MARCELSCHWITTLICK\\2020_DRAWING_PHOTOS\\spirals\\raw\\edit\\144\\"
)

data_map = {}
data_map[yellow] = {}
data_map[blue] = {}
data_map[green] = {}
data_map[red] = {}
data_map[orange] = {}
data_map[black] = {}
data_map[white] = {}
data_map[violet] = {}
data_map[magenta] = {}
data_map[neon_green] = {}
data_map[neon_yellow] = {}
data_map[neon_orange] = {}

# yellow
data_map[yellow][yellow] = {
    "created": "01.08.2020",
    "objktid": 256740,
    "file": f"{path}{yellow}\\{yellow}\\20210902_yy.jpg",
}

data_map[yellow][blue] = {
    "created": "06.05.2021",
    "objktid": 95789,
    "file": f"{path}{yellow}\\{blue}\\20210508_yb.jpg",
}

data_map[yellow][green] = {
    "created": "01.09.2021",
    "objktid": 291319,
    "file": f"{path}{yellow}\\{green}\\20210902_2.jpg",
}

data_map[yellow][red] = {
    "created": "27.04.2021",
    "objktid": 57739,
    "file": f"{path}{yellow}\\{red}\\20210427_yr.jpg",
}

data_map[yellow][orange] = {
    "created": "04.10.2021",
    "objktid": 518083,
    "file": f"{path}{yellow}\\{orange}\\20211012.jpg",
}

data_map[yellow][black] = {
    "created": "10.01.2022",
    "objktid": 658234,
    "file": f"{path}{yellow}\\{black}\\20220111.jpg",
}

data_map[yellow][white] = {
    "created": "22.12.2021",
    "objktid": 667434,
    "file": f"{path}{yellow}\\{white}\\20211225_3.jpg",
}

data_map[yellow][violet] = {
    "created": "03.05.2021",
    "objktid": 239756,
    "file": f"{path}{yellow}\\{violet}\\20210508_yv.jpg",
}

data_map[yellow][magenta] = {
    "created": "06.09.2021",
    "objktid": 291365,
    "file": f"{path}{yellow}\\{magenta}\\20210907_1_ynm.jpg",
}

data_map[yellow][neon_green] = {
    "created": "10.02.2022",
    "objktid": 674580,
    "file": f"{path}{yellow}\\{neon_green}\\20220215.jpg",
}

data_map[yellow][neon_yellow] = {
    "created": "12.11.2021",
    "objktid": 676697,
    "file": f"{path}{yellow}\\{neon_yellow}\\20211125_yny.jpg",
}

data_map[yellow][neon_orange] = {
    "created": "26.01.2022",
    "objktid": 1111,
    "file": f"{path}{yellow}\\{neon_orange}\\20220201.jpg",
}

# blue
data_map[blue][yellow] = {
    "created": "02.03.2021",
    "objktid": 676698,
    "file": f"{path}{blue}\\{yellow}\\20220206.jpg",
}

data_map[blue][blue] = {
    "created": "03.08.2020",
    "objktid": 131715,
    "file": f"{path}{blue}\\{blue}\\20200908_21.jpg",
}

data_map[blue][green] = {
    "created": "17.03.2021",
    "objktid": 1111,
    "file": f"{path}{blue}\\{green}\\20220206.jpg",
}

data_map[blue][red] = {
    "created": "30.09.2021",
    "objktid": 667435,
    "file": f"{path}{blue}\\{red}\\20211017_br.jpg",
}

data_map[blue][orange] = {
    "created": "26.08.2021",
    "objktid": 291350,
    "file": f"{path}{blue}\\{orange}\\20210902_bo.jpg",
}

data_map[blue][black] = {
    "created": "21.04.2021",
    "objktid": 51661,
    "file": f"{path}{blue}\\{black}\\20210427.jpg",
}

data_map[blue][white] = {
    "created": "14.01.2022",
    "objktid": 658235,
    "file": f"{path}{blue}\\{white}\\20220201.jpg",
}

data_map[blue][violet] = {
    "created": "24.11.2021",
    "objktid": 617948,
    "file": f"{path}{blue}\\{violet}\\20211202_bv.jpg",
}

data_map[blue][magenta] = {
    "created": "08.02.2022",
    "objktid": 674581,
    "file": f"{path}{blue}\\{magenta}\\20220215.jpg",
}

data_map[blue][neon_green] = {
    "created": "06.04.2021",
    "objktid": 239702,
    "file": f"{path}{blue}\\{neon_green}\\20210420_4.jpg",
}

data_map[blue][neon_yellow] = {
    "created": "07.06.2021",
    "objktid": 530064,
    "file": f"{path}{blue}\\{neon_yellow}\\20210614_2.jpg",
}

data_map[blue][neon_orange] = {
    "created": "16.06.2021",
    "objktid": 1111,
    "file": f"{path}{blue}\\{neon_orange}\\20220206.jpg",
}

# green
data_map[green][yellow] = {
    "created": "29.02.2021",
    "objktid": 530222,
    "file": f"{path}{green}\\{yellow}\\20220206.jpg",
}

data_map[green][blue] = {
    "created": "25.12.2021",
    "objktid": 674582,
    "file": f"{path}{green}\\{blue}\\20220106.jpg",
}

data_map[green][green] = {
    "created": "01.11.2020",
    "objktid": 1111,
    "file": f"{path}{green}\\{green}\\20200908_5.jpg",
}

data_map[green][red] = {
    "created": "02.09.2021",
    "objktid": 291360,
    "file": f"{path}{green}\\{red}\\20210902_gr.jpg",
}

data_map[green][orange] = {
    "created": "27.01.2022",
    "objktid": 658236,
    "file": f"{path}{green}\\{orange}\\20220201.jpg",
}

data_map[green][black] = {
    "created": "17.11.2021",
    "objktid": 607784,
    "file": f"{path}{green}\\{black}\\20211125_6_gb.jpg",
}

data_map[green][white] = {
    "created": "08.04.2021",
    "objktid": 233987,
    "file": f"{path}{green}\\{white}\\20210420_5.jpg",
}

data_map[green][violet] = {
    "created": "10.05.2021",
    "objktid": 105676,
    "file": f"{path}{green}\\{violet}\\20210524.jpg",
}

data_map[green][magenta] = {
    "created": "18.01.2022",
    "objktid": 667436,
    "file": f"{path}{green}\\{magenta}\\20220201.jpg",
}

data_map[green][neon_green] = {
    "created": "27.09.2021",
    "objktid": 1111,
    "file": f"{path}{green}\\{neon_green}\\20211017_gng.jpg",
}

data_map[green][neon_yellow] = {
    "created": "12.02.2022",
    "objktid": 676700,
    "file": f"{path}{green}\\{neon_yellow}\\20220215.jpg",
}

data_map[green][neon_orange] = {
    "created": "19.03.2021",
    "objktid": 676699,
    "file": f"{path}{green}\\{neon_orange}\\20220206.jpg",
}

# red
data_map[red][yellow] = {
    "created": "03.08.2020",
    "objktid": 667437,
    "file": f"{path}{red}\\{yellow}\\20220206.jpg",
}

data_map[red][blue] = {
    "created": "20.06.2021",
    "objktid": 676701,
    "file": f"{path}{red}\\{blue}\\20220206.jpg",
}

data_map[red][green] = {
    "created": "14.12.2021",
    "objktid": 589822,
    "file": f"{path}{red}\\{green}\\20211216.jpg",
}

data_map[red][red] = {
    "created": "09.04.2021",
    "objktid": 239711,
    "file": f"{path}{red}\\{red}\\20210420_rr.jpg",
}

data_map[red][orange] = {
    "created": "12.04.2021",
    "objktid": 48563,
    "file": f"{path}{red}\\{orange}\\20210420_rno.jpg",
}

data_map[red][black] = {
    "created": "17.05.2021",
    "objktid": 105665,
    "file": f"{path}{red}\\{black}\\20210524_rb.jpg",
}

data_map[red][white] = {
    "created": "03.09.2021",
    "objktid": 291379,
    "file": f"{path}{red}\\{white}\\20210907_rw.jpg",
}

data_map[red][violet] = {
    "created": "13.02.2022",
    "objktid": 674583,
    "file": f"{path}{red}\\{violet}\\20220215.jpg",
}

data_map[red][magenta] = {
    "created": "16.04.2021",
    "objktid": 239737,
    "file": f"{path}{red}\\{magenta}\\20211012.jpg",
}

data_map[red][neon_green] = {
    "created": "21.01.2022",
    "objktid": 658237,
    "file": f"{path}{red}\\{neon_green}\\20220201.jpg",
}

data_map[red][neon_yellow] = {
    "created": "22.06.2021",
    "objktid": 239635,
    "file": f"{path}{red}\\{neon_yellow}\\20210622_rny.jpg",
}

data_map[red][neon_orange] = {
    "created": "03.02.2022",
    "objktid": 1111,
    "file": f"{path}{red}\\{neon_orange}\\20220206_1.jpg",
}

# orange
data_map[orange][yellow] = {
    "created": "23.09.2021",
    "objktid": 674584,
    "file": f"{path}{orange}\\{yellow}\\20211017_2_oy.jpg",
}

data_map[orange][blue] = {
    "created": "10.03.2021",
    "objktid": 1111,
    "file": f"{path}{orange}\\{blue}\\20220206.jpg",
}

data_map[orange][green] = {
    "created": "14.06.2021",
    "objktid": 131818,
    "file": f"{path}{orange}\\{green}\\20210614.jpg",
}

data_map[orange][red] = {
    "created": "15.02.2022",
    "objktid": 1111,
    "file": f"{path}{orange}\\{red}\\20220219.jpg",
}

data_map[orange][orange] = {
    "created": "23.08.2021",
    "objktid": 256768,
    "file": f"{path}{orange}\\{orange}\\20210902_oo.jpg",
}

data_map[orange][black] = {
    "created": "06.01.2022",
    "objktid": 676702,
    "file": f"{path}{orange}\\{black}\\20220106.jpg",
}

data_map[orange][white] = {
    "created": "19.05.2021",
    "objktid": 105591,
    "file": f"{path}{orange}\\{white}\\20210524_ow.jpg",
}

data_map[orange][violet] = {
    "created": "04.02.2022",
    "objktid": 1111,
    "file": f"{path}{orange}\\{violet}\\20220206.jpg",
}

data_map[orange][magenta] = {
    "created": "07.10.2021",
    "objktid": 1111,
    "file": f"{path}{orange}\\{magenta}\\20211012_5.jpg",
}

data_map[orange][neon_green] = {
    "created": "17.01.2022",
    "objktid": 658238,
    "file": f"{path}{orange}\\{neon_green}\\20220201.jpg",
}

data_map[orange][neon_yellow] = {
    "created": "13.09.2021",
    "objktid": 1111,
    "file": f"{path}{orange}\\{neon_yellow}\\20211017_1_ony.jpg",
}

data_map[orange][neon_orange] = {
    "created": "26.11.2021",
    "objktid": 667438,
    "file": f"{path}{orange}\\{neon_orange}\\20211202_ono.jpg",
}

# black
data_map[black][yellow] = {
    "created": "17.06.2021",
    "objktid": 676703,
    "file": f"{path}{black}\\{yellow}\\20220206.jpg",
}

data_map[black][blue] = {
    "created": "23.03.2021",
    "objktid": 530211,
    "file": f"{path}{black}\\{blue}\\20211111_2.jpg",
}

data_map[black][green] = {
    "created": "25.05.2021",
    "objktid": 105732,
    "file": f"{path}{black}\\{green}\\20210530_bg.jpg",
}

data_map[black][red] = {
    "created": "20.04.2021",
    "objktid": 291438,
    "file": f"{path}{black}\\{red}\\20210911.jpg",
}

data_map[black][orange] = {
    "created": "27.10.2021",
    "objktid": 630199,
    "file": f"{path}{black}\\{orange}\\20220106.jpg",
}

data_map[black][black] = {
    "created": "09.08.2020",
    "objktid": 667439,
    "file": f"{path}{black}\\{black}\\20220206.jpg",
}

data_map[black][white] = {
    "created": "01.08.2020",
    "objktid": 256730,
    "file": f"{path}{black}\\{white}\\20210902_bw.jpg",
}

data_map[black][violet] = {
    "created": "27.03.2021",
    "objktid": 674585,
    "file": f"{path}{black}\\{violet}\\20220206.jpg",
}

data_map[black][magenta] = {
    "created": "12.03.2021",
    "objktid": 234017,
    "file": f"{path}{black}\\{magenta}\\20210312_4.jpg",
}

data_map[black][neon_green] = {
    "created": "25.05.2021",
    "objktid": 105740,
    "file": f"{path}{black}\\{neon_green}\\20210530.jpg",
}

data_map[black][neon_yellow] = {
    "created": "04.09.2021",
    "objktid": 291401,
    "file": f"{path}{black}\\{neon_yellow}\\20210907_bny.jpg",
}

data_map[black][neon_orange] = {
    "created": "04.11.2021",
    "objktid": 658239,
    "file": f"{path}{black}\\{neon_orange}\\20211125_bno.jpg",
}

# white

data_map[white][yellow] = {
    "created": "16.01.2022",
    "objktid": 1111,
    "file": f"{path}{white}\\{yellow}\\20220201.jpg",
}

data_map[white][blue] = {
    "created": "29.09.2021",
    "objktid": 1111,
    "file": f"{path}{white}\\{blue}\\20220106.jpg",
}

data_map[white][green] = {
    "created": "15.11.2021",
    "objktid": 1111,
    "file": f"{path}{white}\\{green}\\20220106.jpg",
}

data_map[white][red] = {
    "created": "10.06.2020",
    "objktid": 133550,
    "file": f"{path}{white}\\{red}\\20210614_wr.jpg",
}

data_map[white][orange] = {
    "created": "02.12.2021",
    "objktid": 674586,
    "file": f"{path}{white}\\{orange}\\20211225.jpg",
}

data_map[white][black] = {
    "created": "21.09.2021",
    "objktid": 1111,
    "file": f"{path}{white}\\{black}\\20211017_wb.jpg",
}

data_map[white][white] = {
    "created": "24.08.2020",
    "objktid": 658240,
    "file": f"{path}{white}\\{white}\\20210921_4.jpg",
}

data_map[white][violet] = {
    "created": "30.01.2022",
    "objktid": 667440,
    "file": f"{path}{white}\\{violet}\\20220201.jpg",
}

data_map[white][magenta] = {
    "created": "28.10.2021",
    "objktid": 676704,
    "file": f"{path}{white}\\{magenta}\\20220106.jpg",
}

data_map[white][neon_green] = {
    "created": "09.02.2022",
    "objktid": 1111,
    "file": f"{path}{white}\\{neon_green}\\20220215.jpg",
}

data_map[white][neon_yellow] = {
    "created": "08.09.2021",
    "objktid": 1111,
    "file": f"{path}{white}\\{neon_yellow}\\20220106.jpg",
}

data_map[white][neon_orange] = {
    "created": "16.02.2022",
    "objktid": 1111,
    "file": f"{path}{white}\\{neon_yellow}\\20220219.jpg",
}

# violet

data_map[violet][yellow] = {
    "created": "26.05.2021",
    "objktid": 105713,
    "file": f"{path}{violet}\\{yellow}\\20210530_vy.jpg",
}

data_map[violet][blue] = {
    "created": "21.12.2021",
    "objktid": 667441,
    "file": f"{path}{violet}\\{blue}\\20211225_3.jpg",
}

data_map[violet][green] = {
    "created": "14.04.2021",
    "objktid": 63954,
    "file": f"{path}{violet}\\{green}\\20210419_vg.jpg",
}

data_map[violet][red] = {
    "created": "18.11.2021",
    "objktid": 674587,
    "file": f"{path}{violet}\\{red}\\20220106.jpg",
}

data_map[violet][orange] = {
    "created": "17.02.2022",
    "objktid": 1111,
    "file": f"{path}{violet}\\{orange}\\20220219.jpg",
}

data_map[violet][black] = {
    "created": "21.03.2021",
    "objktid": 530012,
    "file": f"{path}{violet}\\{black}\\20211111.jpg",
}

data_map[violet][white] = {
    "created": "29.05.2021",
    "objktid": 84403,
    "file": f"{path}{violet}\\{white}\\20210508_vw.jpg",
}

data_map[violet][violet] = {
    "created": "01.08.2020",
    "objktid": 256751,
    "file": f"{path}{violet}\\{violet}\\20210902_v.jpg",
}

data_map[violet][magenta] = {
    "created": "13.01.2022",
    "objktid": 658241,
    "file": f"{path}{violet}\\{magenta}\\20220201.jpg",
}

data_map[violet][neon_green] = {
    "created": "29.08.2021",
    "objktid": 291341,
    "file": f"{path}{violet}\\{neon_green}\\20210902_vng.jpg",
}

data_map[violet][neon_yellow] = {
    "created": "19.04.2021",
    "objktid": 46422,
    "file": f"{path}{violet}\\{neon_yellow}\\20210420_vny.jpg",
}

data_map[violet][neon_orange] = {
    "created": "31.01.2022",
    "objktid": 676705,
    "file": f"{path}{violet}\\{neon_orange}\\20220202.jpg",
}

# magenta

data_map[magenta][yellow] = {
    "created": "06.02.2021",
    "objktid": 1075,
    "file": f"{path}{magenta}\\{yellow}\\20220206.jpg",
}

data_map[magenta][blue] = {
    "created": "16.12.2020",
    "objktid": 656939,
    "file": f"{path}{magenta}\\{blue}\\20201217_17.jpg",
}

data_map[magenta][green] = {
    "created": "07.03.2021",
    "objktid": 479021,
    "file": f"{path}{magenta}\\{green}\\20211027.jpg",
}

data_map[magenta][red] = {
    "created": "18.02.2022",
    "objktid": 1111,
    "file": f"{path}{magenta}\\{red}\\20220219.jpg",
}

data_map[magenta][orange] = {
    "created": "09.06.2021",
    "objktid": 239799,
    "file": f"{path}{magenta}\\{orange}\\20210614_nmo.jpg",
}

data_map[magenta][black] = {
    "created": "25.11.2021",
    "objktid": 617947,
    "file": f"{path}{magenta}\\{black}\\20211202_nmb.jpg",
}

data_map[magenta][white] = {
    "created": "27.05.2021",
    "objktid": 105695,
    "file": f"{path}{magenta}\\{white}\\20210530.jpg",
}

data_map[magenta][violet] = {
    "created": "11.12.2021",
    "objktid": 674588,
    "file": f"{path}{magenta}\\{violet}\\20211225_3.jpg",
}

data_map[magenta][magenta] = {
    "created": "01.08.2020",
    "objktid": 256717,
    "file": f"{path}{magenta}\\{magenta}\\20210902_nmnm.jpg",
}

data_map[magenta][neon_green] = {
    "created": "08.03.2021",
    "objktid": 667442,
    "file": f"{path}{magenta}\\{neon_green}\\20220206.jpg",
}

data_map[magenta][neon_yellow] = {
    "created": "25.04.2021",
    "objktid": 239745,
    "file": f"{path}{magenta}\\{neon_yellow}\\20210427_nmny.jpg",
}

data_map[magenta][neon_orange] = {
    "created": "24.01.2022",
    "objktid": 658242,
    "file": f"{path}{magenta}\\{neon_orange}\\20220201.jpg",
}

# neon green

data_map[neon_green][yellow] = {
    "created": "07.02.2021",
    "objktid": 256765,
    "file": f"{path}{neon_green}\\{yellow}\\20210902_ngy.jpg",
}

data_map[neon_green][blue] = {
    "created": "13.10.2020",
    "objktid": 656984,
    "file": f"{path}{neon_green}\\{blue}\\upward_spiral_2020-11-11_21.jpg",
}

data_map[neon_green][green] = {
    "created": "25.01.2022",
    "objktid": 674589,
    "file": f"{path}{neon_green}\\{green}\\20220201.jpg",
}

data_map[neon_green][red] = {
    "created": "30.08.2021",
    "objktid": 291333,
    "file": f"{path}{neon_green}\\{red}\\20210902_ngr.jpg",
}

data_map[neon_green][orange] = {
    "created": "07.01.2022",
    "objktid": 667443,
    "file": f"{path}{neon_green}\\{orange}\\20220111.jpg",
}

data_map[neon_green][black] = {
    "created": "05.05.2021",
    "objktid": 105545,
    "file": f"{path}{neon_green}\\{black}\\20210524_gb.jpg",
}

data_map[neon_green][white] = {
    "created": "07.09.2021",
    "objktid": 291417,
    "file": f"{path}{neon_green}\\{white}\\20210907_1_ngw.jpg",
}

data_map[neon_green][violet] = {
    "created": "1111",
    "objktid": 1111,
    "file": f"{path}{neon_green}\\{violet}\\1111.jpg",
}

data_map[neon_green][magenta] = {
    "created": "05.05.2021",
    "objktid": 95777,
    "file": f"{path}{neon_green}\\{magenta}\\20210508.jpg",
}

data_map[neon_green][neon_green] = {
    "created": "23.04.2021",
    "objktid": 60762,
    "file": f"{path}{neon_green}\\{neon_green}\\20210427_gg (1).jpg",
}

data_map[neon_green][neon_yellow] = {
    "created": "05.01.2022",
    "objktid": 658243,
    "file": f"{path}{neon_green}\\{neon_yellow}\\20220106_5.jpg",
}

data_map[neon_green][neon_orange] = {
    "created": "08.11.2021",
    "objktid": 676706,
    "file": f"{path}{neon_green}\\{neon_orange}\\20211125_ngno.jpg",
}

# neon yellow

data_map[neon_yellow][yellow] = {
    "created": "09.02.2021",
    "objktid": 667444,
    "file": f"{path}{neon_yellow}\\{yellow}\\20220206.jpg",
}

data_map[neon_yellow][blue] = {
    "created": "18.09.2021",
    "objktid": 256794,
    "file": f"{path}{neon_yellow}\\{blue}\\20210902_nyb.jpg",
}

data_map[neon_yellow][green] = {
    "created": "16.01.2021",
    "objktid": 1076,
    "file": f"{path}{neon_yellow}\\{green}\\20210129_6.jpg",
}

data_map[neon_yellow][red] = {
    "created": "12.10.2020",
    "objktid": 1169,
    "file": f"{path}{neon_yellow}\\{red}\\20210419.jpg",
}

data_map[neon_yellow][orange] = {
    "created": "04.05.2021",
    "objktid": 74059,
    "file": f"{path}{neon_yellow}\\{orange}\\20210508_nyo.jpg",
}

data_map[neon_yellow][black] = {
    "created": "03.01.2022",
    "objktid": 658244,
    "file": f"{path}{neon_yellow}\\{black}\\20220106.jpg",
}

data_map[neon_yellow][white] = {
    "created": "1111",
    "objktid": 1111,
    "file": f"{path}{neon_yellow}\\{white}\\1111.jpg",
}

data_map[neon_yellow][violet] = {
    "created": "26.08.2021",
    "objktid": 291345,
    "file": f"{path}{neon_yellow}\\{violet}\\20210902_nyv.jpg",
}

data_map[neon_yellow][magenta] = {
    "created": "15.10.2020",
    "objktid": 568218,
    "file": f"{path}{neon_yellow}\\{magenta}\\20210907_nynm.jpg",
}

data_map[neon_yellow][neon_green] = {
    "created": "02.02.2022",
    "objktid": 676707,
    "file": f"{path}{neon_yellow}\\{neon_green}\\20220206.jpg",
}

data_map[neon_yellow][neon_yellow] = {
    "created": "09.08.2020",
    "objktid": 471762,
    "file": f"{path}{neon_yellow}\\{neon_yellow}\\20210902_ny.jpg",
}

data_map[neon_yellow][neon_orange] = {
    "created": "20.01.2022",
    "objktid": 674590,
    "file": f"{path}{neon_yellow}\\{neon_orange}\\20220201.jpg",
}

# neon orange

data_map[neon_orange][yellow] = {
    "created": "01.02.2022",
    "objktid": 667445,
    "file": f"{path}{neon_orange}\\{yellow}\\20220202.jpg",
}

data_map[neon_orange][blue] = {
    "created": "12.10.2021",
    "objktid": 529880,
    "file": f"{path}{neon_orange}\\{blue}\\20211027_nob.jpg",
}

data_map[neon_orange][green] = {
    "created": "24.08.2021",
    "objktid": 256801,
    "file": f"{path}{neon_orange}\\{green}\\20210902_nog.jpg",
}

data_map[neon_orange][red] = {
    "created": "19.01.2022",
    "objktid": 676708,
    "file": f"{path}{neon_orange}\\{red}\\20220201.jpg",
}

data_map[neon_orange][orange] = {
    "created": "28.04.2021",
    "objktid": 87959,
    "file": f"{path}{neon_orange}\\{orange}\\20210508_noo.jpg",
}

data_map[neon_orange][black] = {
    "created": "10.11.2021",
    "objktid": 659566,
    "file": f"{path}{neon_orange}\\{black}\\20211125_nob.jpg",
}

data_map[neon_orange][white] = {
    "created": "03.12.2021",
    "objktid": 674591,
    "file": f"{path}{neon_orange}\\{white}\\20211225_3.jpg",
}

data_map[neon_orange][violet] = {
    "created": "12.04.2021",
    "objktid": 239714,
    "file": f"{path}{neon_orange}\\{violet}\\20210420_nov.jpg",
}

data_map[neon_orange][magenta] = {
    "created": "09.01.2022",
    "objktid": 658245,
    "file": f"{path}{neon_orange}\\{magenta}\\20220111.jpg",
}

data_map[neon_orange][neon_green] = {
    "created": "1111",
    "objktid": 1111,
    "file": f"{path}{neon_orange}\\{neon_green}\\1111.jpg",
}

data_map[neon_orange][neon_yellow] = {
    "created": "10.10.2021",
    "objktid": 1111,
    "file": f"{path}{neon_orange}\\{neon_yellow}\\20211027_nony.jpg",
}

data_map[neon_orange][neon_orange] = {
    "created": "08.08.2020",
    "objktid": 131720,
    "file": f"{path}{neon_orange}\\{neon_orange}\\20200908_8.jpg",
}

if __name__ == "__main__":
    out_path = "Z:\\144\\"
    # copying all files into one folder and rename
    for k1, v1 in data_map.items():
        for k2, v2 in v1.items():
            print(k1 + " " + k2)
            out = f"{out_path}{k1}_{k2}.jpg"
            print(out)
            if "1111" not in v2["file"]:
                shutil.copyfile(v2["file"], out)
                v2["file"] = f"{k1}_{k2}.jpg"
            else:
                shutil.copyfile(
                    "C:\\Users\\Marcel Schwittlick\\Desktop\\ROHDE-SCHWARZ-XY-Schreiber-Recorder-ZSK-2.jpg",
                    out,
                )
                v2["file"] = f"{k1}_{k2}.jpg"

    with open("z:\\144\\upward_spiral.json", "w") as file:
        file.write(json.dumps(data_map))
