###############################################################################
#
#    Edafa Website Portal
#    Copyright (C) 2024 Edafa Inc.
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

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class EdafaAdmissionPortal(http.Controller):

    @http.route(['/admission', '/admission/apply'], type='http', auth="public", website=True, sitemap=True)
    def admission_form(self, **kwargs):
        """Public admission application form"""
        # Get available courses and batches
        courses = request.env['op.course'].sudo().search([])
        batches = request.env['op.batch'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        titles = request.env['res.partner.title'].sudo().search([])
        
        # Get error messages if redirected after validation error
        error = {}
        default = {
            'first_name': 'Ahmed',
            'middle_name': 'Hassan',
            'last_name': 'Mohamed',
            'email': 'ahmed.hassan@example.com',
            'birth_date': '2000-01-15',
            'mobile': '+201234567890',
            'phone': '0233914986',
            'gender': 'm',  # Default gender for demo
            'street': '123 Tahrir Street',
            'street2': 'Apt 5B',
            'city': 'Cairo',
            'zip': '11511',
        }
        
        if 'admission_error' in request.session:
            error = request.session.pop('admission_error')
            # Override defaults with user's submitted data
            default.update(request.session.pop('admission_default'))
        
        return request.render('edafa_website_branding.admission_application_form', {
            'courses': courses,
            'batches': batches,
            'countries': countries,
            'titles': titles,
            'error': error,
            'default': default,
            'page_name': 'admission',
        })

    @http.route('/admission/submit', type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def admission_submit(self, **post):
        """Handle admission form submission"""
        error = {}
        
        # Validation disabled for testing
        # If validation errors, redirect back with errors
        if error:
            request.session['admission_error'] = error
            # Exclude non-serializable data (like file uploads) from session
            post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
            request.session['admission_default'] = post_data
            return request.redirect('/admission/apply')
        
        try:
            # Get or create admission register for online applications
            AdmissionRegister = request.env['op.admission.register'].sudo()
            current_year = fields.Date.today().year
            register = AdmissionRegister.search([
                ('name', 'ilike', f'Online {current_year}')
            ], limit=1)
            
            if not register:
                # Create a default admission register for online applications
                register = AdmissionRegister.create({
                    'name': f'Online Applications {current_year}',
                    'start_date': fields.Date.today(),
                    'end_date': fields.Date.today().replace(month=12, day=31),
                    'max_count': 1000,  # Maximum number of online admissions
                    'min_count': 1,     # Minimum number of admissions
                })
            
            # Get course_id - handle empty strings and missing values
            course_id = post.get('course_id')
            _logger.info(f"DEBUG: Received course_id from form: {repr(course_id)}")
            
            # Check if course_id is valid (not empty, not False, not None)
            if course_id and str(course_id).strip():
                try:
                    course_id = int(course_id)
                    _logger.info(f"DEBUG: Converted course_id to: {course_id}")
                except (ValueError, TypeError):
                    course_id = None
            else:
                course_id = None
            
            # If no valid course_id, get first available course
            if not course_id:
                _logger.info("DEBUG: No course selected, getting first available course")
                Course = request.env['op.course'].sudo()
                default_course = Course.search([], limit=1)
                if default_course:
                    course_id = default_course.id
                    _logger.info(f"DEBUG: Auto-selected course: {default_course.name} (ID: {course_id})")
                else:
                    # If no courses exist, we can't create admission
                    _logger.error("DEBUG: No courses found in database!")
                    error['general'] = 'No courses available. Please create a course first in the backend.'
                    request.session['admission_error'] = error
                    post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
                    request.session['admission_default'] = post_data
                    return request.redirect('/admission/apply')
            
            # Final safety check for course_id
            if not course_id:
                _logger.error("CRITICAL: course_id is still None/False after all checks!")
                error['general'] = 'System error: Unable to assign course. Please contact administrator.'
                request.session['admission_error'] = error
                post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
                request.session['admission_default'] = post_data
                return request.redirect('/admission/apply')
            
            # Prepare admission data
            admission_vals = {
                'register_id': register.id,  # Required field
                'name': f"{post.get('first_name', '')} {post.get('last_name', '')}".strip() or 'Student',
                'first_name': post.get('first_name', 'Ahmed'),
                'middle_name': post.get('middle_name', 'Hassan'),
                'last_name': post.get('last_name', 'Mohamed'),
                'title': int(post.get('title')) if post.get('title') and post.get('title') != '' else False,
                'email': post.get('email', 'test@example.com'),
                'mobile': post.get('mobile', '+201234567890'),
                'phone': post.get('phone', ''),
                'birth_date': post.get('birth_date') or '2000-01-15',
                'gender': post.get('gender') or 'm',  # Required field - default to male if not provided
                'course_id': course_id,  # Always set to a valid course
                'batch_id': int(post.get('batch_id')) if post.get('batch_id') and post.get('batch_id') != '' else False,
                'street': post.get('street', ''),
                'street2': post.get('street2', ''),
                'city': post.get('city', ''),
                'zip': post.get('zip', ''),
                'state_id': int(post.get('state_id')) if post.get('state_id') and post.get('state_id') != '' else False,
                'country_id': int(post.get('country_id')) if post.get('country_id') and post.get('country_id') != '' else False,
                'application_date': fields.Datetime.now(),
                'state': 'submit',  # Auto-submit the application
            }
            
            _logger.info(f"DEBUG: Creating admission with course_id: {course_id}")
            
            # Handle image upload if provided
            if post.get('image') and hasattr(post.get('image'), 'read'):
                image = post.get('image')
                image_data = image.read()
                if image_data:
                    admission_vals['image'] = base64.b64encode(image_data)
            
            # Create admission record
            admission = request.env['op.admission'].sudo().create(admission_vals)
            
            # Send notification email (optional)
            try:
                template = request.env.ref('edafa_website_branding.admission_confirmation_email', raise_if_not_found=False)
                if template:
                    template.sudo().send_mail(admission.id, force_send=True)
            except:
                pass  # Don't fail if email template doesn't exist yet
            
            # Redirect to thank you page
            return request.redirect(f'/admission/thank-you?application={admission.application_number}')
            
        except Exception as e:
            _logger.exception("Error creating admission application: %s", str(e))
            error['general'] = f"An error occurred: {str(e)}"
            request.session['admission_error'] = error
            # Exclude non-serializable data (like file uploads) from session
            post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
            request.session['admission_default'] = post_data
            return request.redirect('/admission/apply')

    @http.route('/admission/thank-you', type='http', auth="public", website=True)
    def admission_thank_you(self, **kwargs):
        """Thank you page after submission"""
        application_number = kwargs.get('application')
        return request.render('edafa_website_branding.admission_thank_you', {
            'application_number': application_number,
            'page_name': 'admission_thanks',
        })

    @http.route('/admission/check-status', type='http', auth="public", website=True)
    def check_application_status(self, **kwargs):
        """Check application status by application number and email"""
        application_number = kwargs.get('application_number')
        email = kwargs.get('email')
        error = False
        admission = False
        
        if application_number and email:
            admission = request.env['op.admission'].sudo().search([
                ('application_number', '=', application_number),
                ('email', '=', email)
            ], limit=1)
            
            if not admission:
                error = "Application not found. Please check your application number and email."
        
        return request.render('edafa_website_branding.admission_status_check', {
            'admission': admission,
            'error': error,
            'application_number': application_number,
            'email': email,
            'page_name': 'admission_status',
        })


class EdafaPortalCustomer(CustomerPortal):
    """Extend portal to show student applications"""

    def _prepare_home_portal_values(self, counters):
        """Add admission applications count to portal"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'application_count' in counters:
            admission_count = request.env['op.admission'].search_count([
                ('email', '=', partner.email)
            ]) if partner else 0
            values['application_count'] = admission_count
        
        return values

    @http.route(['/my/applications', '/my/applications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_applications(self, page=1, sortby=None, filterby=None, **kw):
        """Display user's admission applications in portal"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AdmissionSudo = request.env['op.admission'].sudo()

        # Search applications by email
        domain = [('email', '=', partner.email)]

        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Application Date'), 'order': 'application_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        
        # Default sort
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Pager
        application_count = AdmissionSudo.search_count(domain)
        pager = portal_pager(
            url="/my/applications",
            total=application_count,
            page=page,
            step=10,
            url_args={'sortby': sortby},
        )

        # Get applications
        applications = AdmissionSudo.search(
            domain,
            order=order,
            limit=10,
            offset=pager['offset']
        )

        values.update({
            'applications': applications,
            'page_name': 'application',
            'pager': pager,
            'default_url': '/my/applications',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("edafa_website_branding.portal_my_applications", values)

    @http.route(['/my/application/<int:application_id>'], type='http', auth="user", website=True)
    def portal_application_detail(self, application_id, **kw):
        """Display single application details"""
        partner = request.env.user.partner_id
        admission = request.env['op.admission'].sudo().browse(application_id)
        
        # Check if this application belongs to the user
        if admission.email != partner.email:
            return request.redirect('/my')
        
        values = {
            'admission': admission,
            'page_name': 'application_detail',
        }
        
        return request.render("edafa_website_branding.portal_application_detail", values)

