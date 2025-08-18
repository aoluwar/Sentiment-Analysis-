#!/usr/bin/env python
"""
Test runner for Sentiment Analysis System

This script provides a convenient way to run tests for the Sentiment Analysis System.
It supports running all tests, specific test modules, or generating coverage reports.
"""

import argparse
import sys
import unittest
import os

def run_tests(test_path=None, verbose=False):
    """Run tests with the specified path"""
    loader = unittest.TestLoader()
    
    if test_path:
        # Run specific test module, class, or method
        if os.path.isfile(test_path):
            # If a file path is provided
            test_dir = os.path.dirname(test_path)
            test_file = os.path.basename(test_path)
            test_module = os.path.splitext(test_file)[0]
            
            # Add the directory to sys.path if it's not already there
            if test_dir and test_dir not in sys.path:
                sys.path.insert(0, test_dir)
                
            tests = loader.loadTestsFromName(test_module)
        else:
            # If a module name is provided (e.g., tests.test_sentiment_analyzer)
            tests = loader.loadTestsFromName(test_path)
    else:
        # Run all tests in the tests directory
        tests = loader.discover('tests')
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    
    # Run tests
    result = runner.run(tests)
    
    # Return exit code based on test result
    return 0 if result.wasSuccessful() else 1

def run_coverage(test_path=None, report_type='report', verbose=False):
    """Run tests with coverage"""
    try:
        import coverage
    except ImportError:
        print("Error: coverage package is not installed. Please install it with 'pip install coverage'.")
        return 1
    
    # Start coverage
    cov = coverage.Coverage()
    cov.start()
    
    # Run tests
    exit_code = run_tests(test_path, verbose)
    
    # Stop coverage
    cov.stop()
    cov.save()
    
    # Generate report
    if report_type == 'report':
        cov.report()
    elif report_type == 'html':
        cov.html_report(directory='htmlcov')
        print("HTML report generated in 'htmlcov' directory. Open 'htmlcov/index.html' in a web browser.")
    elif report_type == 'xml':
        cov.xml_report(outfile='coverage.xml')
        print("XML report generated as 'coverage.xml'.")
    
    return exit_code

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run tests for Sentiment Analysis System')
    parser.add_argument('test_path', nargs='?', help='Specific test module, class, or method to run')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Run with coverage')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--xml', action='store_true', help='Generate XML coverage report')
    
    args = parser.parse_args()
    
    if args.coverage or args.html or args.xml:
        report_type = 'html' if args.html else 'xml' if args.xml else 'report'
        exit_code = run_coverage(args.test_path, report_type, args.verbose)
    else:
        exit_code = run_tests(args.test_path, args.verbose)
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()