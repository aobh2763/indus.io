import argparse
import random
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.permissions import (
	AccessLevel,
	AlertSeverity,
	AlertStatus,
	GlobalRole,
	LogLevel,
	ProductionLineStatus,
	SimulationStatus,
	Visibility,
)
from app.db.database import SessionLocal
from app.modules.analytics import service as analytics_service
from app.modules.analytics.schemas import KPICreate, KPIValueCreate
from app.modules.identity import service as identity_service
from app.modules.identity.models import User
from app.modules.identity.schemas import UserRegister
from app.modules.intelligence import service as intelligence_service
from app.modules.intelligence.schemas import AIAgentCreate, SuggestionCreate
from app.modules.monitoring import service as monitoring_service
from app.modules.monitoring.schemas import AlertCreate
from app.modules.production import service as production_service
from app.modules.production.models import Connection, Machine
from app.modules.production.schemas import (
	ConnectionCreate,
	MachineCreate,
	ProductionLineCreate,
)
from app.modules.project import service as project_service
from app.modules.project.schemas import ProjectAccessCreate, ProjectCreate
from app.modules.simulation import service as simulation_service
from app.modules.simulation.schemas import SimulationCreate, SimulationLogCreate
from app.modules.telemetry import service as telemetry_service
from app.modules.telemetry.schemas import SensorDataCreate


def seed_identity(db: Session):
	users = [
		UserRegister(
			name="Amina Haddad",
			email="amina.haddad@indus.example",
			password="password123",
			role=GlobalRole.ADMIN,
		),
		UserRegister(
			name="Youssef Benali",
			email="youssef.benali@indus.example",
			password="password123",
			role=GlobalRole.USER,
		),
		UserRegister(
			name="Sofia Idrissi",
			email="sofia.idrissi@indus.example",
			password="password123",
			role=GlobalRole.USER,
		),
		UserRegister(
			name="Karim El Mansouri",
			email="karim.elmansouri@indus.example",
			password="password123",
			role=GlobalRole.USER,
		),
	]

	created = []
	for user in users:
		existing = identity_service.get_user_by_email(db, user.email)
		if existing:
			created.append(existing)
		else:
			created.append(identity_service.create_user(db, user))
	return created


def seed_projects(db: Session, owner_id):
	projects = [
		ProjectCreate(
			name="Textile Line A - Cotton Knits",
			description="High-volume cotton knitwear line focused on t-shirts and polos.",
			visibility=Visibility.PRIVATE,
		),
		ProjectCreate(
			name="Textile Line B - Denim",
			description="Denim manufacturing for jeans with heavy stitching processes.",
			visibility=Visibility.PRIVATE,
		),
		ProjectCreate(
			name="Textile Line C - Outdoor Jackets",
			description="Performance fabrics with waterproof coatings and seam sealing.",
			visibility=Visibility.PRIVATE,
		),
	]

	return [project_service.create_project(db, project, user_id=owner_id) for project in projects]


def seed_project_access(db: Session, project_id, users):
	access_entries = [
		ProjectAccessCreate(
			user_id=users[1].id,
			access_level=AccessLevel.SUPERVISOR,
			can_clone=True,
		),
		ProjectAccessCreate(
			user_id=users[2].id,
			access_level=AccessLevel.COLLABORATOR,
			can_clone=False,
		),
		ProjectAccessCreate(
			user_id=users[3].id,
			access_level=AccessLevel.VIEWER,
			can_clone=False,
		),
	]

	return [project_service.create_project_access(db, project_id, entry) for entry in access_entries]


def seed_production_lines(db: Session, project_id):
	lines = [
		ProductionLineCreate(name="Cutting & Preparation", status=ProductionLineStatus.RUNNING),
		ProductionLineCreate(name="Assembly & Stitching", status=ProductionLineStatus.RUNNING),
		ProductionLineCreate(name="Finishing & Packaging", status=ProductionLineStatus.DRAFT),
	]

	return [production_service.create_line(db, project_id, line) for line in lines]


def seed_machines(db: Session, line_id):
	machines = [
		MachineCreate(
			name="Fabric Roll Feeder",
			process="Material Intake",
			manufacturer="TexFeed",
			model_reference="TF-200",
			year_introduced=2018,
			description="Automated fabric roll feeder with tension control.",
			icon="Factory",
			position_x=50.0,
			position_y=80.0,
			parameters={"tension": 12.0, "speed": 1.2},
			is_configured=True,
		),
		MachineCreate(
			name="Laser Cutter",
			process="Cutting",
			manufacturer="CutPro",
			model_reference="LC-500",
			year_introduced=2020,
			description="Precision laser cutting for textile panels.",
			icon="Zap",
			position_x=250.0,
			position_y=80.0,
			parameters={"power": 85.0, "feed_rate": 2.1},
			is_configured=True,
		),
		MachineCreate(
			name="Stitching Station",
			process="Assembly",
			manufacturer="SewTech",
			model_reference="ST-11",
			year_introduced=2017,
			description="Multi-needle stitching station for seams.",
			icon="Wrench",
			position_x=450.0,
			position_y=80.0,
			parameters={"stitch_rate": 1200.0, "thread_tension": 6.0},
			is_configured=True,
		),
		MachineCreate(
			name="Quality Scanner",
			process="Inspection",
			manufacturer="VisionTex",
			model_reference="VT-3D",
			year_introduced=2021,
			description="3D inspection scanner for seam accuracy.",
			icon="Scan",
			position_x=650.0,
			position_y=80.0,
			parameters={"resolution": 0.1, "accuracy": 0.05},
			is_configured=True,
		),
		MachineCreate(
			name="Packaging Conveyor",
			process="Packaging",
			manufacturer="FlowLine",
			model_reference="FL-90",
			year_introduced=2019,
			description="Conveyor for folded garments to packaging.",
			icon="Move3d",
			position_x=850.0,
			position_y=80.0,
			parameters={"belt_speed": 1.4, "load_limit": 25.0},
			is_configured=True,
		),
	]

	created = []
	for machine in machines:
		created.append(
			Machine(
				production_line_id=line_id,
				name=machine.name,
				process=machine.process,
				subprocess=machine.subprocess,
				manufacturer=machine.manufacturer,
				model_reference=machine.model_reference,
				year_introduced=machine.year_introduced,
				description=machine.description,
				icon=machine.icon,
				position_x=machine.position_x,
				position_y=machine.position_y,
				parameters=machine.parameters,
				is_configured=machine.is_configured,
			)
		)
	db.add_all(created)
	db.commit()
	for machine in created:
		db.refresh(machine)
	return created


def seed_connections(db: Session, line_id, machines):
	connections = [
		ConnectionCreate(source_machine_id=machines[0].id, target_machine_id=machines[1].id, weight=1.0),
		ConnectionCreate(source_machine_id=machines[1].id, target_machine_id=machines[2].id, weight=1.0),
		ConnectionCreate(source_machine_id=machines[2].id, target_machine_id=machines[3].id, weight=1.0),
		ConnectionCreate(source_machine_id=machines[3].id, target_machine_id=machines[4].id, weight=1.0),
	]

	created = []
	for connection in connections:
		created.append(
			Connection(
				production_line_id=line_id,
				source_machine_id=connection.source_machine_id,
				target_machine_id=connection.target_machine_id,
				weight=connection.weight,
			)
		)
	db.add_all(created)
	db.commit()
	for connection in created:
		db.refresh(connection)
	return created


def seed_kpis(db: Session, line_id, machines):
	kpis = [
		KPICreate(
			name="OEE",
			machine_id=None,
			formula="availability*performance*quality",
			target_value=85.0,
			unit="%",
		),
		KPICreate(
			name="Throughput",
			machine_id=machines[2].id,
			formula="units/hour",
			target_value=1500.0,
			unit="units/h",
		),
		KPICreate(
			name="Defect Rate",
			machine_id=machines[3].id,
			formula="defects/units",
			target_value=1.5,
			unit="%",
		),
	]

	return [analytics_service.create_kpi(db, line_id, kpi) for kpi in kpis]


def seed_kpi_values(db: Session, kpis, simulation_id=None):
	for kpi in kpis:
		for _ in range(6):
			value = random.uniform(60.0, 95.0) if kpi.name == "OEE" else random.uniform(900.0, 1700.0)
			if kpi.name == "Defect Rate":
				value = random.uniform(0.5, 3.5)
			analytics_service.create_kpi_value(
				db,
				kpi.id,
				KPIValueCreate(simulation_id=simulation_id, value=round(value, 2)),
			)


def seed_telemetry(db: Session, machines):
	sensor_types = ["temperature", "vibration", "throughput", "energy"]
	for machine in machines:
		batch = []
		for _ in range(20):
			sensor_type = random.choice(sensor_types)
			value = random.uniform(20.0, 120.0)
			if sensor_type == "throughput":
				value = random.uniform(50.0, 200.0)
			if sensor_type == "energy":
				value = random.uniform(2.0, 12.0)
			batch.append(
				SensorDataCreate(
					type=sensor_type,
					value=round(value, 2),
					source="simulation",
					quality_score=round(random.uniform(0.85, 0.99), 2),
				)
			)
		telemetry_service.bulk_create_sensor_data(db, machine.id, batch)


def seed_simulation(db: Session, line_id):
	simulation = simulation_service.create_simulation(
		db,
		line_id,
		SimulationCreate(status=SimulationStatus.RUNNING),
	)
	for level, message in [
		(LogLevel.INFO, "Simulation started for textile batch TB-2026-05"),
		(LogLevel.WARNING, "Stitching station thread tension slightly above target"),
		(LogLevel.INFO, "Quality scanner completed scan on batch TB-2026-05"),
	]:
		simulation_service.create_log(
			db,
			simulation.id,
			SimulationLogCreate(level=level, message=message),
		)
	return simulation


def seed_intelligence(db: Session, line_id, machines):
	agent = intelligence_service.create_agent(
		db,
		AIAgentCreate(name="Textile Optimizer", type="recommendation", version="1.0"),
	)
	suggestions = [
		SuggestionCreate(
			ai_agent_id=agent.id,
			machine_id=machines[1].id,
			type="parameter_tune",
			description="Reduce laser cutter feed rate by 5% to improve edge quality.",
			payload={"feed_rate": 1.995},
			confidence=0.82,
		),
		SuggestionCreate(
			ai_agent_id=agent.id,
			machine_id=machines[2].id,
			type="maintenance",
			description="Schedule needle inspection after 8 hours to prevent seam defects.",
			payload={"maintenance_window_hours": 8},
			confidence=0.76,
		),
	]

	return [intelligence_service.create_suggestion(db, line_id, suggestion) for suggestion in suggestions]


def seed_alerts(db: Session, line_id, machines, kpis, simulation_id):
	alerts = [
		AlertCreate(
			production_line_id=line_id,
			machine_id=machines[2].id,
			kpi_id=None,
			simulation_id=simulation_id,
			type="performance",
			severity=AlertSeverity.MEDIUM,
			message="Stitching station throughput below target.",
			status=AlertStatus.OPEN,
		),
		AlertCreate(
			production_line_id=line_id,
			machine_id=machines[3].id,
			kpi_id=kpis[2].id,
			simulation_id=simulation_id,
			type="quality",
			severity=AlertSeverity.HIGH,
			message="Defect rate trending above 2.5%.",
			status=AlertStatus.IN_PROGRESS,
		),
	]

	return [monitoring_service.create_alert(db, alert) for alert in alerts]


def seed_textile_data(db: Session):
	ensure_graph_workspace(db)
	users = seed_identity(db)
	projects = seed_projects(db, owner_id=users[0].id)

	for project in projects:
		seed_project_access(db, project.id, users)
		lines = seed_production_lines(db, project.id)
		for line in lines:
			machines = seed_machines(db, line.id)
			connections = seed_connections(db, line.id, machines)
			sync_graph_from_relational(db, machines, connections)
			kpis = seed_kpis(db, line.id, machines)
			simulation = seed_simulation(db, line.id)
			seed_kpi_values(db, kpis, simulation_id=simulation.id)
			seed_telemetry(db, machines)
			seed_intelligence(db, line.id, machines)
			seed_alerts(db, line.id, machines, kpis, simulation.id)


def parse_args():
	parser = argparse.ArgumentParser(description="Seed textile domain mock data.")
	parser.add_argument(
		"--force",
		action="store_true",
		help="Seed even if users already exist",
	)
	return parser.parse_args()


def ensure_graph_workspace(db: Session):
	db.execute(text("CREATE EXTENSION IF NOT EXISTS age;"))
	db.execute(text("SET search_path = ag_catalog, \"$user\", public;"))
	exists = db.execute(
		text("SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'indus_production' LIMIT 1;")
	).first()
	if not exists:
		db.execute(text("SELECT create_graph('indus_production');"))
	db.commit()


def escape_cypher_value(value: str) -> str:
	return value.replace("'", "''")


def execute_cypher_raw(db: Session, query: str):
	db.execute(text("SET search_path = ag_catalog, \"$user\", public;"))
	db.execute(text(f"SELECT * FROM cypher('indus_production', $$ {query} $$) as (result agtype);"))


def sync_graph_from_relational(db: Session, machines, connections):
	for machine in machines:
		machine_id = escape_cypher_value(str(machine.id))
		name = escape_cypher_value(machine.name)
		process = escape_cypher_value(machine.process or "")
		manufacturer = escape_cypher_value(machine.manufacturer or "")
		execute_cypher_raw(
			db,
			"\n".join(
				[
					f"MERGE (m:Machine {{id: '{machine_id}'}})",
					f"SET m.name = '{name}'",
					f"SET m.process = '{process}'",
					f"SET m.manufacturer = '{manufacturer}'",
				]
			),
		)

	for connection in connections:
		source_id = escape_cypher_value(str(connection.source_machine_id))
		target_id = escape_cypher_value(str(connection.target_machine_id))
		weight = connection.weight or 1.0
		execute_cypher_raw(
			db,
			"\n".join(
				[
					f"MATCH (a:Machine {{id: '{source_id}'}}), (b:Machine {{id: '{target_id}'}})",
					"MERGE (a)-[r:CONNECTION]->(b)",
					f"SET r.weight = {weight}",
				]
			),
		)

	db.commit()


def main():
	args = parse_args()
	db = SessionLocal()
	try:
		if not args.force and db.query(User).count() > 0:
			print("Seed aborted: database already contains users. Use --force to add more.")
			return
		seed_textile_data(db)
		print("Seed complete: textile mock data inserted.")
	finally:
		db.close()


if __name__ == "__main__":
	main()
