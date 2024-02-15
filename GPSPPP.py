import coordinates
import logging

logger = logging.getLogger(__name__)


def GPS_PPP_Calc(ref_file:str, sum_file:str, loc_file:str, out_file_name:str) -> None:
    project = "never found project name"

    logger.debug("Opening Ref file and reading into lines_ref")
    with open(ref_file) as input_file:
        lines_ref = input_file.read().splitlines()
    input_file.close
    logger.debug("lines_ref=")
    logger.debug(lines_ref)
    ref = coordinates.geocentric2grid(float(lines_ref[1]), float(lines_ref[2]))
    ref = lines_ref[1], lines_ref[2], lines_ref[3], str(ref[0]), str(ref[1])
    logger.debug("ref = ")
    logger.debug(ref)

    # reference is now stored in ref[] as:
    # lat long elev E N

    # Sept 7, 2018 - edited as SUM file now has a new format
    # to test if new or old format, in the second line of the file in the old format, it will say it
    # is CSRS-PPP Ver. 1.x

    # first open file and read into an array called lines_ppp
    logger.debug("Opening Sum file and reading into lines_ppp")
    with open(sum_file) as input_file:
        lines_ppp = input_file.read().splitlines()
    logger.debug("lines_ppp=")
    logger.debug(lines_ppp)

    # now test if new or old format file
    if (
        "GPS Precise Point Positioning (CSRS-PPP ver.        1.05/11216/2016-04-21)"
        in lines_ppp[1]
    ):
        old_sum_format = True
        logger.debug("Old format SUM file")
        # old format file
        #
        # this is old code to read
        #
        # in SUM file, Latitude is always on line 218
        # July 13, 2016 - this is not the case when the downloaded and converted file is less than 24hr old
        # to fix this we will iterate through the file and find the line containing:
        #     3.3 Coordinate estimates
        # following this we will find the section
        #     ELLIPSOIDAL
        # our values are the next three lines

        header = "3.3 Coordinate estimates"
        sub_header = "ELLIPSOIDAL"
        i = 0
        while i < len(lines_ppp) - 3 and not header in lines_ppp[i]:
            i += 1
        while i < len(lines_ppp) - 3 and not sub_header in lines_ppp[i]:
            i += 1
        # i is now set such that the next three lines should be our data
        l1 = lines_ppp[i + 1]
        l2 = lines_ppp[i + 2]
        l3 = lines_ppp[i + 3]
        l1 = l1.replace("  ", " ")
        l1 = l1.replace("  ", " ")
        l1 = l1.replace("  ", " ")
        l1 = l1.split(" ")
        l2 = l2.replace("  ", " ")
        l2 = l2.replace("  ", " ")
        l2 = l2.replace("  ", " ")
        l2 = l2.split(" ")
        l3 = l3.replace("  ", " ")
        l3 = l3.replace("  ", " ")
        l3 = l3.replace("  ", " ")
        l3 = l3.split(" ")
        x = coordinates.dms2ddd(float(l1[3]), float(l1[4]), float(l1[5]))
        y = coordinates.dms2ddd(float(l2[3]), float(l2[4]), float(l2[5]))
        xy = coordinates.geocentric2grid(float(x), float(y))
        ppp = [
            l1[3],
            l1[4],
            l1[5],
            l1[9],
            str(xy[0]),
            l2[3],
            l2[4],
            l2[5],
            l2[9],
            str(xy[1]),
            l3[4],
            l3[7],
        ]
        # ppp now holds data in format:
        # Lat-DDD MM SS.SSS Accuracy East Long-DDD MM SS.SSS Accuracy North Elev Accuracy
        #
        # end of old code to read SUM file
        #
    else:
        old_sum_format = False
        logger.debug("New format SUM file")
        # new format file - Sept 7, 2018
        i = 0
        ppp: list[str] = [" "] * 14
        x = y = 0
        while i < len(lines_ppp):
            if lines_ppp[i].split(" ", 1)[0] == "POS":
                # at a position line - figure out which one
                if lines_ppp[i].split(" ")[1] == "LAT":
                    # get Lat data and add to ppp array
                    lat = lines_ppp[i][46:64].strip().split()
                    x = coordinates.dms2ddd(float(lat[0]), float(lat[1]), float(lat[2]))
                    ppp[0] = lat[0]
                    ppp[1] = lat[1]
                    ppp[2] = lat[2]
                    ppp[3] = lines_ppp[i][77:85].strip()
                if lines_ppp[i].split(" ")[1] == "LON":
                    # get Long data and add to ppp array
                    lon = lines_ppp[i][46:64].strip().split()
                    y = coordinates.dms2ddd(float(lon[0]), float(lon[1]), float(lon[2]))
                    ppp[5] = lon[0]
                    ppp[6] = lon[1]
                    ppp[7] = lon[2]
                    ppp[8] = lines_ppp[i][77:85].strip()
                if lines_ppp[i].split(" ")[1] == "HGT":
                    # get ortho Height data and add to ppp array
                    ppp[10] = lines_ppp[i][46:64].strip()
                    ppp[11] = lines_ppp[i][77:85].strip()

            # NEW STUFF
            if lines_ppp[i].split(" ")[0] == "OHT":
                if not lines_ppp[i].split(" ")[1] == "SYST":
                    # get Height data and add to ppp array
                    ppp[12] = lines_ppp[i][28:66].strip()

            if lines_ppp[i].split(" ")[0] == "GHT":
                # get separation value and add to ppp array
                ppp[13] = lines_ppp[i][4:13].strip()

            if lines_ppp[i].split(" ", 1)[0] == "RNX":
                # at the line that lists the input rinex file name - get project nubmer from this
                project = lines_ppp[i].split(" ")[1]
            i += 1
        # have now gone through file - assume x and y contain the geocentric values
        # convert to grid
        xy = coordinates.geocentric2grid(float(x), float(y))
        # add east and north to ppp array
        ppp[4] = str(xy[0])
        ppp[9] = str(xy[1])
        logger.debug("ppp = ")
        logger.debug(ppp)
        #
        # end of new format SUM file
        #

    if old_sum_format:
        # if an old format file get project number. In new format it is alreay there from above
        project = lines_ppp[12]
        project = project[26:]
        project.strip()

    # write project number and HPN Value of Base Position
    if len(project) > 13:
        project = project[:13]
    output_str = [
        "Project Number " + project,
        "",
        "",
    ]
    output_str.append("HPN Value of Base Position:")
    working_string = "latitude:    " + ppp[0] + "-" + ppp[1] + "-" + ppp[2]
    while len(working_string) < 33:
        working_string = working_string + " "
    working_string = working_string + "95% sigma:  " + ppp[3]
    while len(working_string) < 55:
        working_string = working_string + " "
    working_string = working_string + "--> Easting:   " + "{0:.3f}".format(float(ppp[4]))
    output_str.append(working_string)
    working_string = "Longitude:  " + ppp[5] + "-" + ppp[6] + "-" + ppp[7]
    while len(working_string) < 33:
        working_string = working_string + " "
    working_string = working_string + "95% sigma:  " + ppp[8]
    while len(working_string) < 55:
        working_string = working_string + " "
    working_string = working_string + "--> Northing:  " + "{0:.3f}".format(float(ppp[9]))
    output_str.append(working_string)
    working_string = "Ortho Elev:        " + ppp[12]
    while len(working_string) < 33:
        working_string = working_string + " "
    working_string = working_string + "95% sigma:  " + ppp[11]

    # write WS84 Base Position
    output_str.append(working_string)
    output_str.append("")
    output_str.append("")
    output_str.append("WGS84 Base Position:")
    working_string = "Latitude:   " + ref[0]
    while len(working_string) < 55:
        working_string = working_string + " "
    working_string = working_string + "--> Easting:  " + "{0:.3f}".format(float(ref[3]))
    output_str.append(working_string)
    working_string = "Longitude: " + ref[1]
    while len(working_string) < 55:
        working_string = working_string + " "
    working_string = working_string + "--> Northing: " + "{0:.3f}".format(float(ref[4]))
    output_str.append(working_string)
    working_string = "Ell Height: " + ref[2]
    output_str.append(working_string)

    if len(loc_file) > 0:
        # localization file used
        logger.debug("Localization file used, reading loc_file")
        with open(loc_file) as input_file:
            lines_loc = input_file.read().splitlines()
        logger.debug("lines_loc = ")
        logger.debug(lines_loc)
        a = lines_loc[5]
        a = a.split('"')
        a = a[3]
        b = lines_loc[6]
        b = b.split('"')
        b = b[3]
        c = lines_loc[7]
        c = c.split('"')
        c = c[3]
        d = lines_loc[8]
        d = d.split('"')
        d = d[3]
        e = lines_loc[9]
        e = e.split('"')
        e = e[3]
        f = lines_loc[10]
        f = f.split('"')
        f = f[3]
        g = lines_loc[11]
        g = g.split('"')
        g = g[3]
        loc = coordinates.geocentric2grid(float(a), float(b))
        loc = a, b, c, loc[0], loc[1], d, e, f, g
        loc = list(map(str, loc))
        # loc now holds data in format:
        # WGS84shot(Lat-ddd long-ddd elev)-converted(X Y) Geoid-Undulation Local(x y z)
        logger.debug("loc = ")
        logger.debug(loc)

        # write WGS84 Localization Position
        output_str.append("")
        output_str.append("")
        output_str.append("WGS84 Localization Position:")
        working_string = "Latitude:   " + loc[0]
        while len(working_string) < 55:
            working_string = working_string + " "
        working_string = working_string + "--> Easting:  " + "{0:.3f}".format(float(loc[3]))
        output_str.append(working_string)
        working_string = "Longitude: " + loc[1]
        while len(working_string) < 55:
            working_string = working_string + " "
        working_string = working_string + "--> Northing: " + "{0:.3f}".format(float(loc[4]))
        output_str.append(working_string)
        working_string = "Ell Height: " + loc[2]
        output_str.append(working_string)
        output_str.append("")
        output_str.append("")

        # write Position Localized to
        output_str.append("Position Localized to:")
        output_str.append("Easting:    " + loc[6])
        output_str.append("Northing:   " + loc[7])
        output_str.append("Ortho Elev: " + loc[8])
        output_str.append("")
        output_str.append("")

        # write Geoid Undulation Value
        output_str.append("Geoid Undulation Value:  " + ppp[13])
        output_str.append("")
        output_str.append("")

        # write Shift from ADJ-2-HPN
        output_str.append("Shift from ADJ-2-HPN")
        str1 = "Easting:    "
        str2 = "{0:.3f}".format(float(loc[3]) - float(loc[6]) + (float(ppp[4]) - float(ref[3])))
        while len(str1) + len(str2) < 20:
            str1 = str1 + " "
        output_str.append(str1 + str2)
        str1 = "Northing:   "
        str2 = "{0:.3f}".format(float(loc[4]) - float(loc[7]) + (float(ppp[9]) - float(ref[4])))
        while len(str1) + len(str2) < 20:
            str1 = str1 + " "
        output_str.append(str1 + str2)
        str1 = "Elev:   "
        str2 = "{0:.3f}".format(
            float(loc[2]) - float(loc[8]) + (float(ppp[12]) - float(ref[2]))
        )
        logging.debug("elevation calculated as: A-B+C-D")
        logging.debug(loc[2])
        logging.debug(loc[8])
        logging.debug(ppp[12])
        logging.debug(ref[2])

        while len(str1) + len(str2) < 20:
            str1 = str1 + " "
        output_str.append(str1 + str2)
    else:
        output_str.append("")
        output_str.append("")
        output_str.append("Shift from ADJ-2-HPN")
        str1 = "Easting:    "
        str2 = "{0:.3f}".format((float(ppp[4]) - float(ref[3])))
        while len(str1) + len(str2) < 20:
            str1 = str1 + " "
        output_str.append(str1 + str2)
        str1 = "Northing:   "
        str2 = "{0:.3f}".format((float(ppp[9]) - float(ref[4])))
        while len(str1) + len(str2) < 20:
            str1 = str1 + " "
        output_str.append(str1 + str2)
        str1 = "Elev:   "
        str2 = "{0:.3f}".format(float(ppp[10]) - float(ref[2]))
        while len(str1) + len(str2) < 20:
            str1 = str1 + " "
        output_str.append(str1 + str2)

    with open(out_file_name, "w") as input_file:
        for item in output_str:
            input_file.write("%s\n" % item)
