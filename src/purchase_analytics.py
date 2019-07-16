import os
import csv
import math
from sys import argv


# input and output files path
input_opt = argv[1]
input_p = argv[2]
outfile = argv[3]


# loads data from two different input files
# combines them and return a single data dictionary
class DataPrep:
    
    def __init__(self, order_prod_path, product_path):
        # input data files path
        self.order_prod_path = order_prod_path
        self.product_path = product_path
        
        # initiazing two input files dict
        self.order_products = {'order_id': [], 'product_id': [], 'reordered': []}
        self.products = {'product_id': [], 'department_id': []}
    
    def load_order_product(self):
        with open(self.order_prod_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.order_products['order_id'].append(row['order_id'])
                self.order_products['product_id'].append(row['product_id'])
                self.order_products['reordered'].append(row['reordered'])
                
                
    def load_products(self):
        with open(self.product_path, mode='r', encoding='utf8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.products['product_id'].append(row['product_id'])
                self.products['department_id'].append(row['department_id'])
                    
    
    def create_product_department_map(self):
        product_department = dict()
        if self.products is None:
            raise Exception('products dictionary not created yet!')
            
        for pid, did in zip(self.products['product_id'], self.products['department_id']):
            product_department[pid] = did
        return product_department
    
    def combine_inputs(self):
        # final input table (python dict) 
        data_table = {'department_id': [], 'order_id': [], 'product_id': [], 'reordered': []}
        
        # hash map:= {product_id: department_id}
        product_department_map = self.create_product_department_map()
        
        # cross checking each column has equal entry or not
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
        self.table = table  # its combined table of two input files
        # formatting report table as: dictionary of dictionaries or map of has tables
        self.output_table = {'department_id': {'number_of_orders': list(), 
                                               'number_of_first_orders': list(), 
                                               'percentage': None}
                            }
    
    def create_report(self):
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
            
        report = {'department_id': [], 'number_of_orders': [], 'number_of_first_orders': [], 'percentage': []}
        for key in self.output_table.keys():
            report['department_id'].append(int(key))
            report['number_of_orders'].append(self.output_table[key]['number_of_orders'])
            report['number_of_first_orders'].append(self.output_table[key]['number_of_first_orders'])
            report['percentage'].append(self.output_table[key]['percentage'])
    
        return report
                    
    # bubble sorting O(n^2)
    # can be used better sorting O(nlog(n))
    # but since its it's about sorting just about 20 rows: I am using bubble sort
    def bubble_sort(self, arr):
        # arr = list of [index, department_id]
        n = len(arr)  
        for i in range(n): 
            # Last i elements are already in place 
            for j in range(0, n-i-1): 
                # Swap if the element found is greater than the next element 
                if arr[j][1] > arr[j+1][1] : 
                    arr[j][0], arr[j+1][0] = arr[j+1][0], arr[j][0]
                    arr[j][1], arr[j+1][1] = arr[j+1][1], arr[j][1]
        return arr
                    
    def sort_by_department(self, report):
        # sorting by department_id
        department_ids = [[index, did] for index, did in enumerate(report['department_id'])]
        sortedby_dids = self.bubble_sort(department_ids)
        sortby_indices = [sortedby_dids[i][0] for i in range(len(sortedby_dids))]
        # preparing sorted array
        report_array = []
        for index in sortby_indices:
            # checking if number_of_orders > 0. Otherwise, skipping the department listing.
            if report['number_of_orders'][index] > 0:
                report_array.append([report['department_id'][index], report['number_of_orders'][index], 
                             report['number_of_first_orders'][index], report['percentage'][index]])
        return report_array
                
    def create_ouput_file(self, report_array, outfile):
        with open(outfile, mode='w') as file:
            writer = csv.DictWriter(file, fieldnames=['department_id', 'number_of_orders', 
                                                          'number_of_first_orders', 'percentage'])
            writer.writeheader()
            for row in report_array:
                writer.writerow({'department_id': row[0], 'number_of_orders': row[1], 'number_of_first_orders': row[2], 'percentage': row[3]})
        file.close()


# running the data preparation and analytics
def main(input_opt, input_p, outfile):
    # data preparation
    data = DataPrep(input_opt, input_p)
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
    main(input_opt, input_p, outfile)
