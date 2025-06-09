"""
Communication Service for Independent Dealer Prospector
Handles Twilio (voice/SMS) and SendGrid (email) integrations with logging.
"""

import os
import logging
from typing import Dict, List
from datetime import datetime
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, Content
import phonenumbers
from email_validator import validate_email, EmailNotValidError

from services.crm_service import crm_service

logger = logging.getLogger(__name__)

class CommunicationService:
    """Service for multi-channel communications"""
    
    def __init__(self):
        self.twilio_client = None
        self.sendgrid_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize communication clients"""
        try:
            # Twilio setup
            twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
            twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
            if twilio_sid and twilio_token:
                self.twilio_client = TwilioClient(twilio_sid, twilio_token)
                self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            # SendGrid setup
            sendgrid_key = os.getenv('SENDGRID_API_KEY')
            if sendgrid_key:
                self.sendgrid_client = SendGridAPIClient(api_key=sendgrid_key)
                self.from_email = os.getenv('FROM_EMAIL', 'sales@yourdomain.com')
                self.from_name = os.getenv('FROM_NAME', 'Sales Team')
            
        except Exception as e:
            logger.error(f"Error initializing communication clients: {e}")
    
    # PHONE CALL OPERATIONS
    
    def make_call(self, prospect_id: int, to_number: str, 
                  message: str = None, callback_url: str = None) -> Dict:
        """Initiate a phone call to prospect"""
        if not self.twilio_client:
            return {'success': False, 'error': 'Twilio not configured'}
        
        try:
            # Validate phone number
            parsed_number = phonenumbers.parse(to_number, "US")
            if not phonenumbers.is_valid_number(parsed_number):
                return {'success': False, 'error': 'Invalid phone number'}
            
            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            
            # Default message for calls
            if not message:
                message = ("Hello, this is a sales representative calling about "
                          "automotive dealership solutions. Please hold while we connect you.")
            
            # Create TwiML for the call
            twiml_url = self._create_call_twiml(message, callback_url)
            
            # Make the call
            call = self.twilio_client.calls.create(
                to=formatted_number,
                from_=self.twilio_phone,
                url=twiml_url,
                status_callback=callback_url
            )
            
            # Log the communication
            comm_data = {
                'channel': 'call',
                'direction': 'outbound',
                'status': 'initiated',
                'message': message,
                'external_id': call.sid,
                'created_at': datetime.now()
            }
            
            crm_service.log_communication(prospect_id, comm_data)
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status,
                'to': formatted_number
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error making call: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error making call: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_call_twiml(self, message: str, callback_url: str = None) -> str:
        """Create TwiML URL for call handling"""
        # In production, you'd host TwiML endpoints
        # For now, return a simple TwiML that plays the message
        return f"http://twimlets.com/message?Message%5B0%5D={message}"
    
    # SMS OPERATIONS
    
    def send_sms(self, prospect_id: int, to_number: str, message: str) -> Dict:
        """Send SMS to prospect"""
        if not self.twilio_client:
            return {'success': False, 'error': 'Twilio not configured'}
        
        try:
            # Validate phone number
            parsed_number = phonenumbers.parse(to_number, "US")
            if not phonenumbers.is_valid_number(parsed_number):
                return {'success': False, 'error': 'Invalid phone number'}
            
            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            
            # Send SMS
            sms = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=formatted_number
            )
            
            # Log the communication
            comm_data = {
                'channel': 'sms',
                'direction': 'outbound',
                'status': sms.status,
                'message': message,
                'external_id': sms.sid,
                'created_at': datetime.now()
            }
            
            crm_service.log_communication(prospect_id, comm_data)
            
            return {
                'success': True,
                'message_sid': sms.sid,
                'status': sms.status,
                'to': formatted_number
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {'success': False, 'error': str(e)}
    
    # EMAIL OPERATIONS
    
    def send_email(self, prospect_id: int, to_email: str, subject: str, 
                   content: str, template_id: str = None, 
                   personalization_data: Dict = None) -> Dict:
        """Send email to prospect"""
        if not self.sendgrid_client:
            return {'success': False, 'error': 'SendGrid not configured'}
        
        try:
            # Validate email
            try:
                validated_email = validate_email(to_email)
                to_email = validated_email.email
            except EmailNotValidError:
                return {'success': False, 'error': 'Invalid email address'}
            
            # Create email
            if template_id:
                # Use dynamic template
                message = Mail(
                    from_email=From(self.from_email, self.from_name),
                    to_emails=To(to_email)
                )
                message.template_id = template_id
                
                if personalization_data:
                    message.dynamic_template_data = personalization_data
            else:
                # Use plain content
                message = Mail(
                    from_email=From(self.from_email, self.from_name),
                    to_emails=To(to_email),
                    subject=Subject(subject),
                    content=Content("text/html", content)
                )
            
            # Send email
            response = self.sendgrid_client.send(message)
            
            # Log the communication
            comm_data = {
                'channel': 'email',
                'direction': 'outbound',
                'status': 'sent' if response.status_code in [200, 202] else 'failed',
                'subject': subject,
                'message': content,
                'external_id': response.headers.get('X-Message-Id'),
                'created_at': datetime.now()
            }
            
            crm_service.log_communication(prospect_id, comm_data)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'to': to_email
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'success': False, 'error': str(e)}
    
    # TEMPLATE OPERATIONS
    
    def get_email_templates(self) -> List[Dict]:
        """Get available email templates"""
        # Basic templates - in production, fetch from SendGrid
        return [
            {
                'id': 'intro',
                'name': 'Introduction Email',
                'subject': 'Automotive Solutions for {{dealership_name}}',
                'description': 'Initial outreach to new prospects'
            },
            {
                'id': 'followup',
                'name': 'Follow-up Email',
                'subject': 'Following up on {{dealership_name}}',
                'description': 'Follow-up after initial contact'
            },
            {
                'id': 'meeting',
                'name': 'Meeting Request',
                'subject': 'Meeting Request - {{dealership_name}}',
                'description': 'Request for in-person or virtual meeting'
            }
        ]
    
    def get_sms_templates(self) -> List[Dict]:
        """Get available SMS templates"""
        return [
            {
                'id': 'intro',
                'name': 'Introduction SMS',
                'message': 'Hi {{contact_name}}, I help auto dealers improve operations. Quick 5min call?',
                'description': 'Initial SMS outreach'
            },
            {
                'id': 'followup',
                'name': 'Follow-up SMS',
                'message': 'Hi {{contact_name}}, following up on my message about dealership solutions.',
                'description': 'Follow-up SMS'
            }
        ]
    
    def render_template(self, template: str, data: Dict) -> str:
        """Simple template rendering"""
        for key, value in data.items():
            template = template.replace(f'{{{{{key}}}}}', str(value))
        return template
    
    # COMMUNICATION HISTORY
    
    def get_prospect_communications(self, prospect_id: int) -> List[Dict]:
        """Get communication history for prospect"""
        communications = crm_service.get_prospect_communications(prospect_id)
        
        return [
            {
                'id': comm.id,
                'channel': comm.channel,
                'direction': comm.direction,
                'status': comm.status,
                'subject': comm.subject,
                'message': comm.message,
                'response': comm.response,
                'created_at': comm.created_at,
                'external_id': comm.external_id
            }
            for comm in communications
        ]
    
    # WEBHOOK HANDLERS
    
    def handle_twilio_webhook(self, webhook_data: Dict) -> Dict:
        """Handle Twilio webhook for call/SMS status updates"""
        try:
            external_id = webhook_data.get('CallSid') or webhook_data.get('MessageSid')
            status = webhook_data.get('CallStatus') or webhook_data.get('MessageStatus')
            
            if external_id and status:
                # Update communication status in database
                # This would need to be implemented in CRM service
                logger.info(f"Twilio webhook: {external_id} status {status}")
                
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error handling Twilio webhook: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_sendgrid_webhook(self, webhook_data: List[Dict]) -> Dict:
        """Handle SendGrid webhook for email events"""
        try:
            for event in webhook_data:
                message_id = event.get('sg_message_id')
                event_type = event.get('event')
                timestamp = event.get('timestamp')
                
                if message_id and event_type:
                    # Update communication status in database
                    logger.info(f"SendGrid webhook: {message_id} event {event_type} at {timestamp}")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error handling SendGrid webhook: {e}")
            return {'success': False, 'error': str(e)}
    
    # UTILITY METHODS
    
    def validate_phone_number(self, phone: str, country: str = "US") -> Dict:
        """Validate and format phone number"""
        try:
            parsed = phonenumbers.parse(phone, country)
            if phonenumbers.is_valid_number(parsed):
                return {
                    'valid': True,
                    'formatted': phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.E164
                    ),
                    'national': phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.NATIONAL
                    )
                }
            else:
                return {'valid': False, 'error': 'Invalid phone number'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def validate_email_address(self, email: str) -> Dict:
        """Validate email address"""
        try:
            validated = validate_email(email)
            return {
                'valid': True,
                'email': validated.email,
                'normalized': validated.email.lower()
            }
        except EmailNotValidError as e:
            return {'valid': False, 'error': str(e)}

# Global communication service instance
communication_service = CommunicationService() 