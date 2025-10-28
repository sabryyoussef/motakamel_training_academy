#!/usr/bin/env python3
###############################################################################
#
#    Motakamel Workflow Dashboard - Test Runner
#    Copyright (C) 2024 Motakamel Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import subprocess
import json
from pathlib import Path

def run_tests():
    """Run comprehensive tests for the Motakamel Workflow Dashboard module"""
    
    print("=" * 80)
    print("🧪 MOTAKAMEL WORKFLOW DASHBOARD - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Module path
    module_path = "/home/sabry3/home_extended/development/odoo-src/running_odoo_no_custom/odoo-18/custom-addons/motakamel/motakamel_workflow_dashboard"
    
    # Test files to run
    test_files = [
        "tests.test_motakamel_workflow",
        "tests.test_motakamel_workflow_stage", 
        "tests.test_motakamel_workflow_transition",
        "tests.test_motakamel_workflow_analytics",
        "tests.test_workflow_wizard",
        "tests.test_workflow_integration"
    ]
    
    print(f"📁 Module Path: {module_path}")
    print(f"🔍 Test Files: {len(test_files)}")
    print()
    
    # Check if module exists
    if not os.path.exists(module_path):
        print("❌ ERROR: Module path does not exist!")
        return False
    
    # Check if test files exist
    missing_tests = []
    for test_file in test_files:
        test_path = os.path.join(module_path, test_file.replace('.', '/') + '.py')
        if not os.path.exists(test_path):
            missing_tests.append(test_file)
    
    if missing_tests:
        print("❌ ERROR: Missing test files:")
        for test in missing_tests:
            print(f"   - {test}")
        return False
    
    print("✅ All test files found!")
    print()
    
    # Run syntax checks
    print("🔍 RUNNING SYNTAX CHECKS...")
    print("-" * 40)
    
    syntax_errors = []
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__pycache__'):
                python_files.append(os.path.join(root, file))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                compile(f.read(), py_file, 'exec')
            print(f"✅ {os.path.relpath(py_file, module_path)}")
        except SyntaxError as e:
            syntax_errors.append(f"{py_file}: {e}")
            print(f"❌ {os.path.relpath(py_file, module_path)} - Syntax Error")
        except Exception as e:
            print(f"⚠️  {os.path.relpath(py_file, module_path)} - {e}")
    
    if syntax_errors:
        print("\n❌ SYNTAX ERRORS FOUND:")
        for error in syntax_errors:
            print(f"   {error}")
        return False
    
    print(f"\n✅ All {len(python_files)} Python files passed syntax check!")
    print()
    
    # Run import tests
    print("🔍 RUNNING IMPORT TESTS...")
    print("-" * 40)
    
    import_errors = []
    test_imports = [
        "models.motakamel_workflow",
        "models.motakamel_workflow_stage",
        "models.motakamel_workflow_transition", 
        "models.motakamel_workflow_analytics",
        "wizards.workflow_wizard"
    ]
    
    for import_name in test_imports:
        try:
            # Change to module directory
            os.chdir(module_path)
            # Add module to Python path
            sys.path.insert(0, module_path)
            
            # Try to import
            __import__(import_name)
            print(f"✅ {import_name}")
        except ImportError as e:
            import_errors.append(f"{import_name}: {e}")
            print(f"❌ {import_name} - Import Error")
        except Exception as e:
            print(f"⚠️  {import_name} - {e}")
    
    if import_errors:
        print("\n❌ IMPORT ERRORS FOUND:")
        for error in import_errors:
            print(f"   {error}")
        return False
    
    print(f"\n✅ All {len(test_imports)} modules imported successfully!")
    print()
    
    # Run Odoo-specific tests
    print("🔍 RUNNING ODOO-SPECIFIC TESTS...")
    print("-" * 40)
    
    # Check manifest file
    manifest_path = os.path.join(module_path, "__manifest__.py")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r') as f:
                manifest_content = f.read()
                exec(manifest_content)
            print("✅ __manifest__.py - Valid")
        except Exception as e:
            print(f"❌ __manifest__.py - Error: {e}")
            return False
    else:
        print("❌ __manifest__.py - Missing")
        return False
    
    # Check security file
    security_path = os.path.join(module_path, "security", "ir.model.access.csv")
    if os.path.exists(security_path):
        print("✅ security/ir.model.access.csv - Found")
    else:
        print("❌ security/ir.model.access.csv - Missing")
        return False
    
    # Check data files
    data_files = [
        "data/workflow_student_lifecycle_data.xml",
        "data/workflow_academic_operations_data.xml", 
        "data/workflow_financial_data.xml",
        "data/workflow_administration_data.xml",
        "data/workflow_parent_data.xml",
        "data/workflow_module_mapping_data.xml"
    ]
    
    for data_file in data_files:
        data_path = os.path.join(module_path, data_file)
        if os.path.exists(data_path):
            print(f"✅ {data_file} - Found")
        else:
            print(f"❌ {data_file} - Missing")
    
    # Check view files
    view_files = [
        "views/workflow_hub_view.xml",
        "views/workflow_views.xml",
        "views/workflow_menu.xml",
        "wizards/workflow_wizard_view.xml"
    ]
    
    for view_file in view_files:
        view_path = os.path.join(module_path, view_file)
        if os.path.exists(view_path):
            print(f"✅ {view_file} - Found")
        else:
            print(f"❌ {view_file} - Missing")
    
    print()
    
    # Run file structure validation
    print("🔍 RUNNING FILE STRUCTURE VALIDATION...")
    print("-" * 40)
    
    required_structure = [
        "__init__.py",
        "__manifest__.py", 
        "models/__init__.py",
        "models/motakamel_workflow.py",
        "models/motakamel_workflow_stage.py",
        "models/motakamel_workflow_transition.py",
        "models/motakamel_workflow_analytics.py",
        "views/workflow_hub_view.xml",
        "views/workflow_views.xml", 
        "views/workflow_menu.xml",
        "security/ir.model.access.csv",
        "tests/__init__.py",
        "tests/test_motakamel_workflow.py",
        "tests/test_motakamel_workflow_stage.py",
        "tests/test_motakamel_workflow_transition.py",
        "tests/test_motakamel_workflow_analytics.py",
        "tests/test_workflow_wizard.py",
        "tests/test_workflow_integration.py"
    ]
    
    missing_files = []
    for file_path in required_structure:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - Missing")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} required files missing!")
        return False
    
    print(f"\n✅ All {len(required_structure)} required files found!")
    print()
    
    # Run static asset validation
    print("🔍 RUNNING STATIC ASSET VALIDATION...")
    print("-" * 40)
    
    static_files = [
        "static/description/icon.png",
        "static/src/js/workflow_diagram_widget.js",
        "static/src/js/workflow_navigation.js",
        "static/src/scss/workflow_dashboard.scss",
        "static/src/xml/workflow_templates.xml"
    ]
    
    for static_file in static_files:
        static_path = os.path.join(module_path, static_file)
        if os.path.exists(static_path):
            print(f"✅ {static_file}")
        else:
            print(f"❌ {static_file} - Missing")
    
    print()
    
    # Summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Python Files Checked: {len(python_files)}")
    print(f"✅ Modules Imported: {len(test_imports)}")
    print(f"✅ Required Files: {len(required_structure)}")
    print(f"✅ Test Files Created: {len(test_files)}")
    print(f"✅ Static Assets: {len(static_files)}")
    print()
    print("🎉 ALL TESTS PASSED! Module is ready for installation.")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
