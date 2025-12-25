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
        """Public admission application form - Now uses multi-step wizard (Phase 1)"""
        # Get available courses, batches, programs
        courses = request.env['op.course'].sudo().search([])
        batches = request.env['op.batch'].sudo().search([])
        programs = request.env['op.program'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        titles = request.env['res.partner.title'].sudo().search([])
        
        # Demo data for testing
        default = {
            'first_name': 'Ahmed',
            'middle_name': 'Hassan',
            'last_name': 'Mohamed',
            'email': 'ahmed.hassan@example.com',
            'birth_date': '2000-01-15',
            'mobile': '+966 59 921 4084',
            'phone': '+966 59 921 4084',
            'gender': 'm',
            'street': '123 Tahrir Street',
            'street2': 'Apt 5B',
            'city': 'Cairo',
            'zip': '11511',
            'prev_institute_id': 'Cairo Secondary School',
            'prev_course_id': 'High School Diploma',
            'prev_result': '85%',
            'family_business': 'Self-employed',
            'family_income': '50000',
        }
        
        # Use wizard template instead of old form
        return request.render('edafa_website_branding.admission_application_wizard', {
            'courses': courses,
            'batches': batches,
            'programs': programs,
            'countries': countries,
            'titles': titles,
            'default': default,
            'page_name': 'admission_wizard',
        })

    @http.route(['/admission/apply/classic'], type='http', auth="public", website=True)
    def admission_form_classic(self, **kwargs):
        """Original single-page form (kept for compatibility)"""
        # Get available courses, batches, programs
        courses = request.env['op.course'].sudo().search([])
        batches = request.env['op.batch'].sudo().search([])
        programs = request.env['op.program'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        titles = request.env['res.partner.title'].sudo().search([])
        
        error = {}
        default = {
            'first_name': 'Ahmed',
            'middle_name': 'Hassan',
            'last_name': 'Mohamed',
            'email': 'ahmed.hassan@example.com',
            'birth_date': '2000-01-15',
            'mobile': '+966 59 921 4084',
            'phone': '+966 59 921 4084',
            'gender': 'm',
            'street': '123 Tahrir Street',
            'street2': 'Apt 5B',
            'city': 'Cairo',
            'zip': '11511',
            'prev_institute_id': 'Cairo Secondary School',
            'prev_course_id': 'High School Diploma',
            'prev_result': '85%',
            'family_business': 'Self-employed',
            'family_income': '50000',
        }
        
        if 'admission_error' in request.session:
            error = request.session.pop('admission_error')
            default.update(request.session.pop('admission_default'))
        
        return request.render('edafa_website_branding.admission_application_form', {
            'courses': courses,
            'batches': batches,
            'programs': programs,
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
            # NOTE: Don't pass False for Many2one fields - just omit them if empty
            admission_vals = {
                'register_id': register.id,  # Required field
                'name': f"{post.get('first_name', '')} {post.get('last_name', '')}".strip() or 'Student',
                'first_name': post.get('first_name', 'Ahmed'),
                'middle_name': post.get('middle_name', 'Hassan'),
                'last_name': post.get('last_name', 'Mohamed'),
                'email': post.get('email', 'test@example.com'),
                'mobile': post.get('mobile', '+966 59 921 4084'),
                'phone': post.get('phone', ''),
                'birth_date': post.get('birth_date') or '2000-01-15',
                'gender': post.get('gender') or 'm',  # Required field - default to male if not provided
                'course_id': course_id,  # Always set to a valid course
                'street': post.get('street', ''),
                'street2': post.get('street2', ''),
                'city': post.get('city', ''),
                'zip': post.get('zip', ''),
                'application_date': fields.Datetime.now(),
                'state': 'submit',  # Auto-submit the application
                # Previous education fields (optional)
                'prev_institute_id': post.get('prev_institute_id', ''),
                'prev_course_id': post.get('prev_course_id', ''),
                'prev_result': post.get('prev_result', ''),
                # Family information fields (optional)
                'family_business': post.get('family_business', ''),
                # Payment fields (set default application fee)
                'application_fee': 50.0,  # Default $50 application fee
                'payment_status': 'unpaid',
            }
            
            # Handle family income (float field)
            if post.get('family_income') and post.get('family_income') != '':
                try:
                    admission_vals['family_income'] = float(post.get('family_income'))
                except (ValueError, TypeError):
                    pass
            
            # Only add Many2one fields if they have valid values
            if post.get('title') and post.get('title') != '':
                try:
                    admission_vals['title'] = int(post.get('title'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('program_id') and post.get('program_id') != '':
                try:
                    admission_vals['program_id'] = int(post.get('program_id'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('batch_id') and post.get('batch_id') != '':
                try:
                    admission_vals['batch_id'] = int(post.get('batch_id'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('state_id') and post.get('state_id') != '':
                try:
                    admission_vals['state_id'] = int(post.get('state_id'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('country_id') and post.get('country_id') != '':
                try:
                    admission_vals['country_id'] = int(post.get('country_id'))
                except (ValueError, TypeError):
                    pass
            
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
        
        # Get admission object to show payment option
        admission = None
        if application_number:
            admission = request.env['op.admission'].sudo().search([
                ('application_number', '=', application_number)
            ], limit=1)
        
        return request.render('edafa_website_branding.admission_thank_you', {
            'application_number': application_number,
            'admission': admission,
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


    @http.route('/admission/check-email', type='json', auth='public', csrf=False)
    def check_email(self, email):
        """Check if email already has an active application"""
        exists = request.env['op.admission'].sudo().search_count([
            ('email', '=', email),
            ('state', 'not in', ['cancel', 'reject'])
        ]) > 0
        return {'exists': exists}

    @http.route('/admission/save-draft', type='json', auth='public')
    def save_draft(self, **data):
        """Save application draft to session"""
        try:
            request.session['admission_draft'] = data
            request.session['admission_draft_timestamp'] = fields.Datetime.now().isoformat()
            return {
                'status': 'saved',
                'timestamp': request.session['admission_draft_timestamp']
            }
        except Exception as e:
            _logger.exception("Error saving draft: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/admission/load-draft', type='json', auth='public')
    def load_draft(self):
        """Load saved application draft from session"""
        draft = request.session.get('admission_draft', {})
        timestamp = request.session.get('admission_draft_timestamp', '')
        return {
            'formData': draft,
            'timestamp': timestamp
        }

    # ============================================
    # PAYMENT ROUTES - Phase 2
    # ============================================

    @http.route('/admission/<int:admission_id>/payment', type='http', 
                auth='public', website=True)
    def admission_payment_page(self, admission_id, access_token=None, **kwargs):
        """
        Display payment page for application fee.
        Can be accessed publicly with access_token or by logged-in owner.
        """
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('http_routing.404')
        
        # Verify access (temporarily permissive for testing - remove in production)
        # TODO: Re-enable strict access control after testing
        # if not self._check_admission_access(admission, access_token):
        #     return request.render('http_routing.403')
        
        # Create invoice if doesn't exist and fee > 0
        if not admission.invoice_id and admission.application_fee > 0:
            try:
                admission.action_create_invoice()
            except Exception as e:
                _logger.exception("Error creating invoice: %s", str(e))
                error_html = f"""
                <div class="container mt-5">
                    <div class="alert alert-danger">
                        <h4>Error Creating Invoice</h4>
                        <p>{str(e)}</p>
                        <a href="/admission/apply" class="btn btn-primary">Submit New Application</a>
                    </div>
                </div>
                """
                return request.make_response(error_html, headers=[('Content-Type', 'text/html')])
        
        # Get available payment providers
        payment_providers = request.env['payment.provider'].sudo().search([
            ('state', '=', 'enabled'),
            ('is_published', '=', True),
        ])
        
        return request.render('edafa_website_branding.admission_payment_page', {
            'admission': admission,
            'invoice': admission.invoice_id,
            'payment_providers': payment_providers,
            'access_token': access_token or '',
            'page_name': 'payment',
        })

    @http.route('/admission/<int:admission_id>/create-payment-transaction', 
                type='json', auth='public')
    def create_payment_transaction(self, admission_id, provider_id, access_token=None):
        """
        Create payment.transaction for online payment.
        Links transaction to admission for tracking.
        """
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return {'error': 'Admission not found'}
        
        if not self._check_admission_access(admission, access_token):
            return {'error': 'Access denied'}
        
        try:
            # Ensure partner exists
            if not admission.partner_id:
                partner = request.env['res.partner'].sudo().create({
                    'name': admission.name,
                    'email': admission.email,
                    'phone': admission.mobile,
                    'street': admission.street,
                    'city': admission.city,
                    'zip': admission.zip,
                    'country_id': admission.country_id.id if admission.country_id else False,
                    'state_id': admission.state_id.id if admission.state_id else False,
                })
                admission.partner_id = partner.id
            
            # Ensure invoice exists
            if not admission.invoice_id:
                admission.action_create_invoice()
            
            # Create payment transaction
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if not provider.exists():
                return {'error': 'Payment provider not found'}
            
            tx = request.env['payment.transaction'].sudo().create({
                'provider_id': provider.id,
                'amount': admission.application_fee,
                'currency_id': admission.currency_id.id,
                'partner_id': admission.partner_id.id,
                'reference': admission.application_number,
                'invoice_ids': [(4, admission.invoice_id.id)] if admission.invoice_id else [],
                'landing_route': f'/admission/{admission.id}/payment/success?access_token={access_token or ""}',
            })
            
            admission.payment_transaction_id = tx.id
            
            _logger.info(f'Payment transaction created for {admission.application_number}: {tx.reference}')
            
            return {
                'success': True,
                'transaction_id': tx.id,
                'redirect_url': f'/payment/pay?reference={tx.reference}',
            }
            
        except Exception as e:
            _logger.exception("Error creating payment transaction: %s", str(e))
            return {'error': str(e)}

    @http.route('/admission/<int:admission_id>/payment/success', 
                type='http', auth='public', website=True)
    def payment_success(self, admission_id, access_token=None, **kwargs):
        """
        Payment success callback page.
        Updates admission status after successful payment.
        """
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('http_routing.404')
        
        # Update payment status from transaction
        if admission.payment_transaction_id:
            admission._update_payment_status_from_transaction()
        
        return request.render('edafa_website_branding.admission_payment_success', {
            'admission': admission,
            'transaction': admission.payment_transaction_id,
            'access_token': access_token or '',
            'page_name': 'payment_success',
        })

    @http.route('/admission/<int:admission_id>/payment/cancel', 
                type='http', auth='public', website=True)
    def payment_cancel(self, admission_id, access_token=None, **kwargs):
        """Payment cancelled callback"""
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('http_routing.404')
        
        return request.render('edafa_website_branding.admission_payment_cancel', {
            'admission': admission,
            'access_token': access_token or '',
            'page_name': 'payment_cancel',
        })

    # ============================================
    # HELPER METHODS
    # ============================================

    def _check_admission_access(self, admission, access_token=None):
        """
        Check if current user can access admission.
        Returns True if:
        - User is logged in and is the partner owner
        - Public user provides valid access_token
        """
        # Debug logging
        _logger.info(f"Checking access for admission {admission.id}")
        _logger.info(f"Access token provided: {access_token}")
        _logger.info(f"Admission access token: {admission.access_token}")
        _logger.info(f"Is public user: {request.env.user._is_public()}")
        
        if request.env.user._is_public():
            # Public user needs valid access token
            if not access_token:
                _logger.warning(f"No access token provided for admission {admission.id}")
                return False
            
            # Check if admission has access token (new field might not be set on old records)
            if not admission.access_token:
                _logger.warning(f"Admission {admission.id} has no access_token - generating one")
                admission.sudo()._generate_access_token()
            
            is_valid = access_token == admission.access_token
            _logger.info(f"Token validation result: {is_valid}")
            return is_valid
        else:
            # Logged in user must be the owner
            is_owner = admission.partner_id == request.env.user.partner_id or \
                       admission.email == request.env.user.partner_id.email
            _logger.info(f"Logged in user ownership check: {is_owner}")
            return is_owner


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

