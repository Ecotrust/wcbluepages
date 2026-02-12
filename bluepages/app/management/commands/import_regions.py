from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Import Regions. 1 argument: a zipped shapefile in EPSG:3857"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        import sys
        from io import BytesIO
        import zipfile
        import shapefile
        from app.models import Region
        from address.models import State

        # Check out Input
        try:
            in_file_name = options["file"]
        except IndexError:
            self.stdout.write(
                "--- ERROR: You must provide the location of the zipped shapefile! ---"
            )
            sys.exit()
        if not zipfile.is_zipfile(in_file_name):
            self.stdout.write(
                "--- ERROR: Input shapefile (1st arg) must be a zipfile ---"
            )
            sys.exit()
        zip_format = None
        try:
            shape_zip = zipfile.ZipFile(in_file_name)
            zip_format = zipfile.ZIP_STORED
        except NotImplementedError:
            formats = [zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA]
            for zipFormat in formats:
                try:
                    shape_zip = zipfile.ZipFile(in_file_name, compression=zipFormat)
                    zip_format = zipFormat
                    break
                except NotImplementedError:
                    pass
                except RuntimeError:
                    format_name = "unknown"
                    if zipFormat == zipfile.ZIP_DEFLATED:
                        format_name = "zlib"
                    if zipFormat == zipfile.ZIP_BZIP2:
                        format_name = "bz2"
                    if zipFormat == zipfile.ZIP_LZMA:
                        format_name = "lzma"
                    self.stdout.write("--- ERROR: Zipfile format not supported ---")
                    self.stdout.write("--- Please install: %s ---" % format_name)
                    sys.exit()
        if zip_format is None:
            self.stdout.write("--- ERROR: Unable to open zipfile ---")
            sys.exit()

        with zipfile.ZipFile(in_file_name, "r", zip_format) as zipshape:
            shapefiles = [
                fname for fname in zipshape.namelist() if fname[-4:] == ".shp"
            ]
            dbffiles = [fname for fname in zipshape.namelist() if fname[-4:] == ".dbf"]
            shxfiles = [fname for fname in zipshape.namelist() if fname[-4:] == ".shx"]
            prjfiles = [fname for fname in zipshape.namelist() if fname[-4:] == ".prj"]

            if len(shapefiles) != 1:
                if len(shapefiles) < 1:
                    self.stdout.write(
                        "--- ERROR: zipfile does not contain a .shp file ---"
                    )
                if len(shapefiles) > 1:
                    self.stdout.write(
                        "--- ERROR: zipfile contains multiple .shp files ---"
                    )
                sys.exit()
            if len(dbffiles) != 1:
                if len(dbffiles) < 1:
                    self.stdout.write(
                        "--- ERROR: zipfile does not contain a .dbf file ---"
                    )
                if len(dbffiles) > 1:
                    self.stdout.write(
                        "--- ERROR: zipfile contains multiple .dbf files ---"
                    )
                sys.exit()
            if len(shxfiles) != 1:
                if len(shxfiles) < 1:
                    self.stdout.write(
                        "--- ERROR: zipfile does not contain a .shx file ---"
                    )
                if len(shxfiles) > 1:
                    self.stdout.write(
                        "--- ERROR: zipfile contains multiple .shx files ---"
                    )
                sys.exit()
            if len(prjfiles) != 1:
                if len(prjfiles) < 1:
                    self.stdout.write(
                        "--- ERROR: zipfile does not contain a .prj file ---"
                    )
                    prjfiles = [None]
                if len(prjfiles) > 1:
                    self.stdout.write(
                        "--- ERROR: zipfile contains multiple .prj files ---"
                    )
                sys.exit()

            shape = shapefile.Reader(
                shp=BytesIO(zipshape.read(shapefiles[0])),
                shx=BytesIO(zipshape.read(shxfiles[0])),
                prj=BytesIO(zipshape.read(prjfiles[0])) if prjfiles[0] else None,
                dbf=BytesIO(zipshape.read(dbffiles[0])),
            )
            fieldsArray = [x[0] for x in shape.fields]

            id_field = "CODE"
            name_field = "Name"
            depth_type_field = "PTYPE"
            id_num_field = "NUMB"
            states_field = "States"

            # fields has DeletionFlag as first item, not included in records indeces
            unit_id_index = fieldsArray.index(id_field) - 1
            unit_name_index = fieldsArray.index(name_field) - 1
            unit_depth_type_index = fieldsArray.index(depth_type_field) - 1
            unit_id_num_index = fieldsArray.index(id_num_field) - 1
            unit_states_index = fieldsArray.index(states_field) - 1

            from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
            import json

            import_count = 0

            self.stdout.write("Updating Regions...")
            for shapeRecord in shape.shapeRecords():
                unit_id = shapeRecord.record[unit_id_index]
                unit_name = shapeRecord.record[unit_name_index]
                unit_depth_type = shapeRecord.record[unit_depth_type_index]
                unit_id_num = shapeRecord.record[unit_id_num_index]
                unit_states = shapeRecord.record[unit_states_index].split(",")

                shape_dict = shapeRecord.shape.__geo_interface__.copy()
                shape_dict["crs"] = settings.IMPORT_SRID
                geometry = GEOSGeometry(json.dumps(shape_dict))
                if geometry.geom_type == "Polygon":
                    multiGeometry = MultiPolygon((geometry))
                elif geometry.geom_type == "MultiPolygon":
                    multiGeometry = geometry
                else:
                    self.stdout.write(
                        "--- ERROR: Features in shapefile are not all (Multi)Polygons ---"
                    )
                    sys.exit()
                region, created = Region.objects.get_or_create(id=str(unit_id))
                region.geometry = multiGeometry
                region.name = unit_name
                region.depth_type = unit_depth_type
                region.id_num = unit_id_num

                region.states.clear()

                for state in unit_states:
                    try:
                        state_record = State.objects.get(
                            postal_code=state.strip().upper()
                        )
                        region.states.add(state_record)
                    except Exception:
                        print(
                            f'Error adding state "{state}" to region "{region.id}: {region.name}"'
                        )
                        pass

                region.save()

                import_count += 1

        self.stdout.write("Successfully added %s Region records" % import_count)
