from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.schema.roles import RoleSchema
from app.models import db
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.errors import NotFoundError
from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint, request, jsonify
from flask_jwt import jwt_required
from app.models.users_events_role import UsersEventsRoles as UER
from app.models.role import Role
from app.api.helpers.db import save_to_db

role_misc_routes = Blueprint('role_misc', __name__, url_prefix='/v1')

class RoleList(ResourceList):
    """
    List and create role
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}


class RoleDetail(ResourceDetail):
    """
    Role detail by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('role_invite_id') is not None:
                role_invite = safe_query(self, RoleInvite, 'id', view_kwargs['role_invite_id'], 'role_invite_id')
                if role_invite.role_id is not None:
                    view_kwargs['id'] = role_invite.role_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('users_events_role_id') is not None:
                users_events_role = safe_query(self, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
                'users_events_role_id')
                if users_events_role.role_id is not None:
                    view_kwargs['id'] = users_events_role.role_id
                else:
                    view_kwargs['id'] = None

    def before_update_object(self, role, data, view_kwargs):
        """
        Method to edit object
        :param role:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('name'):
            if data['name'] in ['organizer', 'coorganizer', 'registrar', 'moderator', 'attendee', 'track_organizer']:
                raise UnprocessableEntity({'data': 'name'}, "The given name cannot be updated")

    def before_delete_object(self, obj, kwargs):
        """
        method to check proper resource name before deleting
        :param obj:
        :param kwargs:
        :return:
        """
        if obj.name in ['organizer', 'coorganizer', 'registrar', 'moderator', 'attendee', 'track_organizer']:
            raise UnprocessableEntity({'data': 'name'}, "The resource with given name cannot be deleted")

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role,
                  'methods': {
                      'before_get_object': before_get_object
                  }}

@role_misc_routes.route('/change-organiser', methods=['POST'])
# @jwt_required()
def change_organiser():
    print('\n\nYou have reached organiser changer\n\n')
    original_organiser_id = request.json['data']['original_org_id']
    new_organiser_id = request.json['data']['new_org_id']
    event_id = request.json['data']['event_id']
    try:
        role_entry_organiser_to_coorg = UER.query.filter_by(user_id=original_organiser_id,
                                                            event_id=event_id,
                                                            role_id=1).one()
        print(role_entry_organiser_to_coorg)
        role_entry_organiser_to_coorg.role_id = 2
        save_to_db(role_entry_organiser_to_coorg)
        print(role_entry_organiser_to_coorg)
        
        role_entry_coorg_to_organiser = UER.query.filter_by(user_id=new_organiser_id,
                                                            event_id=event_id,
                                                            role_id=2).one()
        print(role_entry_coorg_to_organiser)
        role_entry_coorg_to_organiser.role_id = 1
        save_to_db(role_entry_coorg_to_organiser)
        print(role_entry_coorg_to_organiser)
        
    except NoResultFound:
        return NotFoundError({'source': ''}, 'Role Entry not found').respond()

    return jsonify({
        "message": 'you have reached the completion'
    })