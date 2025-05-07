import main as atomfoxapi

atom = atomfoxapi.Atom('Basic ZX...') # Authorization token

logs = atom.get_employee_activity_log()

for log in logs:
    print(f'{log.admin_email} - {log.vehicle_nr} | {log.status_from} → {log.status_to}')

# this sctipt get employee activity log of atom
# example output:
# office@foxscooters.md - FF0001 | Maintenance → Available
# office@foxscooters.md - FF0001 | Available → Transportation