from re import search
from unittest import mock

from boto3 import client, session
from moto import mock_rds

from prowler.providers.aws.lib.audit_info.models import AWS_Audit_Info

AWS_ACCOUNT_NUMBER = "123456789012"
AWS_REGION = "us-east-1"


class Test_rds_instance_minor_version_upgrade_enabled:
    # Mocked Audit Info
    def set_mocked_audit_info(self):
        audit_info = AWS_Audit_Info(
            session_config=None,
            original_session=None,
            audit_session=session.Session(
                profile_name=None,
                botocore_session=None,
                region_name=AWS_REGION,
            ),
            audited_account=AWS_ACCOUNT_NUMBER,
            audited_user_id=None,
            audited_partition="aws",
            audited_identity_arn=None,
            profile=None,
            profile_region=AWS_REGION,
            credentials=None,
            assumed_role_info=None,
            audited_regions=None,
            organizations_metadata=None,
            audit_resources=None,
        )
        return audit_info

    @mock_rds
    def test_rds_no_instances(self):
        from prowler.providers.aws.services.rds.rds_service import RDS

        audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.rds.rds_instance_minor_version_upgrade_enabled.rds_instance_minor_version_upgrade_enabled.rds_client",
                new=RDS(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.rds.rds_instance_minor_version_upgrade_enabled.rds_instance_minor_version_upgrade_enabled import (
                    rds_instance_minor_version_upgrade_enabled,
                )

                check = rds_instance_minor_version_upgrade_enabled()
                result = check.execute()

                assert len(result) == 0

    @mock_rds
    def test_rds_instance_no_auto_upgrade(self):
        conn = client("rds", region_name=AWS_REGION)
        conn.create_db_instance(
            DBInstanceIdentifier="db-master-1",
            AllocatedStorage=10,
            Engine="postgres",
            DBName="staging-postgres",
            DBInstanceClass="db.m1.small",
        )

        from prowler.providers.aws.services.rds.rds_service import RDS

        audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.rds.rds_instance_minor_version_upgrade_enabled.rds_instance_minor_version_upgrade_enabled.rds_client",
                new=RDS(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.rds.rds_instance_minor_version_upgrade_enabled.rds_instance_minor_version_upgrade_enabled import (
                    rds_instance_minor_version_upgrade_enabled,
                )

                check = rds_instance_minor_version_upgrade_enabled()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "FAIL"
                assert search(
                    "does not have minor version upgrade enabled",
                    result[0].status_extended,
                )
                assert result[0].resource_id == "db-master-1"

    @mock_rds
    def test_rds_instance_with_auto_upgrade(self):
        conn = client("rds", region_name=AWS_REGION)
        conn.create_db_instance(
            DBInstanceIdentifier="db-master-1",
            AllocatedStorage=10,
            Engine="postgres",
            DBName="staging-postgres",
            DBInstanceClass="db.m1.small",
            AutoMinorVersionUpgrade=True,
        )

        from prowler.providers.aws.services.rds.rds_service import RDS

        audit_info = self.set_mocked_audit_info()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.rds.rds_instance_minor_version_upgrade_enabled.rds_instance_minor_version_upgrade_enabled.rds_client",
                new=RDS(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.rds.rds_instance_minor_version_upgrade_enabled.rds_instance_minor_version_upgrade_enabled import (
                    rds_instance_minor_version_upgrade_enabled,
                )

                check = rds_instance_minor_version_upgrade_enabled()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "PASS"
                assert search(
                    "has minor version upgrade enabled",
                    result[0].status_extended,
                )
                assert result[0].resource_id == "db-master-1"
