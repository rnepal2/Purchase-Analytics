# standard libraries
import csv
from sys import argv


# input and output files path
order_products_path = argv[1]
products_path = argv[2]
outfile = argv[3]


class DataPrep:
    '''
       loads data from two different input files: joined with department_id column
       combines them and return a single data dictionary
    '''
    
    def __init__(self, order_products_path, products_path):
        '''few initializations'''
        # input data files path
        self.order_products_path = order_products_path
        self.products_path = products_path
        
        # initiazing two input dictionaries (formatted)
        # each columns are stored in a list of the dictionary
        self.order_products = {'order_id': [], 'product_id': [], 'reordered': []}
        self.products = {'product_id': [], 'department_id': []}
    
    def load_order_product(self):
        '''loads order_products input file'''
        with open(self.order_products_path, 'r', encoding='utf-8) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.order_products['order_id'].append(row['order_id'])
                self.order_products['product_id'].append(row['product_id'])
                self.order_products['reordered'].append(row['reordered'])
        csv_file.close()
                
                
    def load_products(self):
        '''loads the product input file'''
        with open(self.products_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.products['product_id'].append(row['product_id'])
                self.products['department_id'].append(row['department_id'])
        csv_file.close()
                    
    
    def create_product_department_map(self):
        '''creates a dict map between product_id and department_id'''
        product_department = dict()
        if self.products is None:
            raise ValueError('products input file is not read yet!')
            
        for prod_id, depart_id in zip(self.products['product_id'], self.products['department_id']):
            product_department[prod_id] = depart_id
        return product_department
    
    def join_inputs(self):
        '''join two input tables based on matchinng product_id
           returns the combined table as a dict
        '''
        # storing combined data files into joined_table dictionary
        joined_table = {'department_id': [], 'order_id': [], 'product_id': [], 'reordered': []}
        
        # product->department map:= {product_id: department_id}
        product_department_map = self.create_product_department_map()
        
        # checking whether each column has equal number of entry or not
        assert len(self.order_products['product_id']) == len(self.order_products['reordered'])
        assert len(self.order_products['reordered']) == len(self.order_products['order_id'])
        
        # populating joined_table
        for order_id, prod_id, reord in zip(self.order_products['order_id'], self.order_products['product_id'], self.order_products['reordered']):
            joined_table['department_id'].append(product_department_map[prod_id])
            joined_table['order_id'].append(order_id)
            joined_table['product_id'].append(prod_id)
            joined_table['reordered'].append(reord)
        return joined_table


class Analytics:
    
    def __init__(self, joined_table):
        '''initialize with: joined_table from DataPrep'''
        self.joined_table = joined_table  

    
    def create_report(self):
        '''use the combined input file: creates the report'''
        # formatting output report table as: dictionary of dictionaries.
        report_dict =  {'department_id': {
                                            'number_of_orders': list(), 
                                            'number_of_first_orders': list(), 
                                            'percentage': None
                                         }
                       }
        for depart_id, reord in zip(self.joined_table['department_id'], self.joined_table['reordered']):
            if depart_id not in report_dict.keys():
                if reord == '0':
                    # just initializing percentage: will calculate later after populating 
                    # all the records into report_dict
                    report_dict[depart_id] = {
                                              'number_of_orders': [1],
                                              'number_of_first_orders': [1],
                                              'percentage': 0
                                             }
                if reord == '1':
                    report_dict[depart_id] = {
                                              'number_of_orders': [1],
                                              'number_of_first_orders': [0],
                                              'percentage': 0
                                             }
            else: 
                if reord == '0':
                    report_dict[depart_id]['number_of_orders'].append(1)
                    report_dict[depart_id]['number_of_first_orders'].append(1),
                if reord == '1':
                    report_dict[depart_id]['number_of_orders'].append(1)
                    report_dict[depart_id]['number_of_first_orders'].append(0)
                    
        # delete the first entry: used for formatting output (not a real entry)
        del report_dict['department_id']
        
        # summing up reordered numbers-> to get first time order numbers
        for key in report_dict.keys():
            number_of_orders = sum(report_dict[key]['number_of_orders'])
            number_of_first_orders = sum(report_dict[key]['number_of_first_orders'])
            percentage = round(number_of_first_orders / number_of_orders, 2)
            report_dict[key] = {
                                 'number_of_orders': number_of_orders,
                                 'number_of_first_orders': number_of_first_orders,
                                 'percentage': percentage
                                }
        
        # creating final report: as a dictionary with columns of required report 
        report = {'department_id': [], 'number_of_orders': [], 'number_of_first_orders': [], 'percentage': []}
        for key in report_dict.keys():
            report['department_id'].append(int(key))
            report['number_of_orders'].append(report_dict[key]['number_of_orders'])
            report['number_of_first_orders'].append(report_dict[key]['number_of_first_orders'])
            report['percentage'].append(report_dict[key]['percentage'])
    
        return report
                    
    def bubble_sort(self, report):
        '''
           helper function for sorting
           bubble sorting O(n^2): Used to sort report based on department_id
           can be used better sorting O(nlog(n)): used bubble sort for small # of  departments
        '''
        # report = list of lists: [index, department_id]
        n = len(report)  
        for i in range(n): 
            # Last i elements are already in place 
            for j in range(0, n-i-1): 
                # swap if the element found is greater than the next element 
                if report[j][1] > report[j+1][1] : 
                    report[j][0], report[j+1][0] = report[j+1][0], report[j][0]
                    report[j][1], report[j+1][1] = report[j+1][1], report[j][1]
        return report
                    
    def sort_by_department(self, report):
        '''sorts the report created by department_id'''
        department_ids = [[index, did] for index, did in enumerate(report['department_id'])]
        sortedby_dids = self.bubble_sort(department_ids)
        sortby_indices = [sortedby_dids[i][0] for i in range(len(sortedby_dids))]
        # preparing sorted report: returning as a list[lists]
        report_array = []
        for index in sortby_indices:
            # checking if number_of_orders > 0. Otherwise, skipping the department listing.
            if report['number_of_orders'][index] > 0:
                report_array.append([report['department_id'][index], report['number_of_orders'][index], 
                             report['number_of_first_orders'][index], report['percentage'][index]])
        return report_array
                
    def create_ouput_file(self, report_array, outfile):
        '''takes required sorted report array: writes into a csv file.'''
        with open(outfile, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['department_id', 'number_of_orders', 
                                                          'number_of_first_orders', 'percentage'])
            writer.writeheader()
            for row in report_array:
                writer.writerow({
                                    'department_id': row[0], 
                                    'number_of_orders': row[1], 
                                    'number_of_first_orders': row[2], 
                                    'percentage': row[3]
                                })
        csv_file.close()


# running the data preparation and analytics
def main():
    # data preparation
    data = DataPrep(order_products_path, products_path)
    # load both the data files
    data.load_order_product()
    data.load_products()
    # combining the input data into a single table
    table = data.join_inputs()

    # analytics and creating report
    analyse = Analytics(table)
    report = analyse.create_report()
    sorted_report = analyse.sort_by_department(report)
    # creating the output file
    analyse.create_ouput_file(sorted_report, outfile)


if __name__ == "__main__":
    main()
