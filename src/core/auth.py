from djangosaml2.backends import Saml2Backend


class SamlRoleBackend(Saml2Backend):
    def authenticate(
        self,
        request,
        session_info=None,
        attribute_mapping=None,
        create_unknown_user=True,
        assertion_info=None,
        **kwargs,
    ):
        user = super().authenticate(
            request=request,
            session_info=session_info,
            attribute_mapping=attribute_mapping,
            create_unknown_user=create_unknown_user,
            assertion_info=assertion_info,
            **kwargs,
        )

        if user is not None and request is not None and session_info:
            request.session["saml_roles"] = self._extract_roles(session_info.get("ava", {}))

        return user

    def _extract_roles(self, attributes):
        roles = []
        for key in ("roles", "role", "Role"):
            values = attributes.get(key, [])
            if isinstance(values, str):
                values = [values]
            roles.extend(values)

        return sorted({role for role in roles if role})
