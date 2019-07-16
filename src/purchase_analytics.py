# standard libraries
import os
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
        self.order_products = {'order_id': [], 'product_id': [], 'reordered': []}
        self.products = {'product_id': [], 'department_id': []}
    
    def load_order_product(self):
        '''loads order_products input file'''
        with open(self.order_products_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.order_products['order_id'].append(row['order_id'])
                self.order_products['product_id'].append(row['product_id'])
                self.order_products['reordered'].append(row['reordered'])
                
                
    def load_products(self):
        '''loads the product input file'''
        with open(self.products_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.products['product_id'].append(row['product_id'])
                self.products['department_id'].append(row['department_id'])
                    
    
    def create_product_department_map(self):
        '''creates a dict map between product_id and department_id'''
        product_department = dict()
        if self.products is None:
            raise ValueError('products input file is not read yet!')
            
        for pid, did in zip(self.products['product_id'], self.products['department_id']):
            product_department[pid] = did
        return product_department
    
    def combine_inputs(self):
        '''join two input tables based on product_id
           returns the combined table as a dict
        '''
        # storing combined data files into data_table dictionary
        data_table = {'department_id': [], 'order_id': [], 'product_id': [], 'reordered': []}
        
        # product->department map:= {product_id: department_id}
        product_department_map = self.create_product_department_map()
        
        # checking whether each column has equal number of entry or not
        assert len(self.order_products['product_id']) == len(self.order_products['reordered'])
        assert len(self.order_products['reordered']) == len(self.order_products['order_id'])
        
        # populating data_table
        for oid, pid, re in zip(self.order_products['order_id'], self.order_products['product_id'], self.order_products['reordered']):
            data_table['department_id'].append(product_department_map[pid])
            data_table['order_id'].append(oid)
            data_table['product_id'].append(pid)
            data_table['reordered'].append(re)
        return data_table


class Analytics:
    
    def __init__(self, table):
        '''initializing input combined data table and  formatted output'''
        self.table = table  # its combined table of two input files
        # formatting output report table as: dictionary of dictionaries.
        self.output_table = {'department_id': {'number_of_orders': list(), 
                                               'number_of_first_orders': list(), 
                                               'percentage': None}
                            }
    
    def create_report(self):
        '''use the combined input file: creates the report'''
        for did, re in zip(self.table['department_id'], self.table['reordered']):

            if did not in self.output_table.keys():
                if re == '0':
                    self.output_table[did] = {'number_of_orders': [1],
                                         'number_of_first_orders': [1],
                                         'percentage': 0}
                if re == '1':
                    self.output_table[did] = {'number_of_orders': [1],
                                         'number_of_first_orders': [0],
                                         'percentage': 0}

            else: #if did in self.output_table.keys():
                if re == '0':
                    self.output_table[did]['number_of_orders'].append(1)
                    self.output_table[did]['number_of_first_orders'].append(1),
                if re == '1':
                    self.output_table[did]['number_of_orders'].append(1)
                    self.output_table[did]['number_of_first_orders'].append(0)
                    
        # delete the first entry: used for formatting output (not a real entry)
        del self.output_table['department_id']
        
        # summing up order numbers and first time order numbers
        for key in self.output_table.keys():
            self.output_table[key] = {'number_of_orders': sum(self.output_table[key]['number_of_orders']),
                                 'number_of_first_orders': sum(self.output_table[key]['number_of_first_orders']),
                                 'percentage': round(sum(self.output_table[key]['number_of_first_orders']) / \
                                                     sum(self.output_table[key]['number_of_orders']), 2)}
        
        # creating final report: as a dictionary with columns of required report 
        report = {'department_id': [], 'number_of_orders': [], 'number_of_first_orders': [], 'percentage': []}
        for key in self.output_table.keys():
            report['department_id'].append(int(key))
            report['number_of_orders'].append(self.output_table[key]['number_of_orders'])
            report['number_of_first_orders'].append(self.output_table[key]['number_of_first_orders'])
            report['percentage'].append(self.output_table[key]['percentage'])
    
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
        '''takes required report list: saves into a csv file at outfile.'''
        with open(outfile, mode='w') as file:
            writer = csv.DictWriter(file, fieldnames=['department_id', 'number_of_orders', 
                                                          'number_of_first_orders', 'percentage'])
            writer.writeheader()
            for row in report_array:
                writer.writerow({'department_id': row[0], 'number_of_orders': row[1], 'number_of_first_orders': row[2], 'percentage': row[3]})
        file.close()


# running the data preparation and analytics
def main(order_products_path, products_path, outfile):
    # data preparation
    data = DataPrep(order_products_path, products_path)
    # load both the data files
    data.load_order_product()
    data.load_products()
    # combining the input data into a single table
    table = data.combine_inputs()

    # analytics and creating report
    analyse = Analytics(table)
    report = analyse.create_report()
    sorted_report = analyse.sort_by_department(report)
    # creating the output file
    analyse.create_ouput_file(sorted_report, outfile)


if __name__ == "__main__":
    main(order_products_path, products_path, outfile)
