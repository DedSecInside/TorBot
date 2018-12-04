def main():

    file = open_file()
    data = create_dictionary(file)
    get_country_total(data)




def open_file(file):
    fp = []
    fp = open("diabetes_data_small.csv",encoding ="windows-1252") 




def create_dictionary(file):

    for line_list in file
        country = line_list[1]
        region = line_list[2]
        age_group = line_list[3]
        gender = line_list[4]
        geographic_area = line_list[5]
        diabetes = int(float(line_list[6])*1000) population = int(float(line_list[7])*1000)
        tup = (gender, geographic_area, diabetes, population)




def get_country_total(data):
    print(data)
