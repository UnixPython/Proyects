from api_client import (
    get_job_token_scope,
    get_job_info,
    try_cross_project_access,
)

from comparator import (
    get_latest_result,
    load_result,
    compare_results,
    flag_anomalies,
    save_results
)


def run_audit_cycle(project_id1, project_id2) -> None:
    private_token = "TU_PRIVATE_TOKEN"
    job_token = "TU_JOB_TOKEN"

    try:
        job_info = get_job_info(job_token)
        scope = get_job_token_scope(private_token, project_id1, project_id2)
        across = try_cross_project_access(job_token, project_id2)
    except Exception as err:
        print(f"Fallo: {err}")
        job_info = {}
        scope = ({}, {})
        across = {}

    resultados = {
        "job_token_scope": scope,
        "job_info": job_info,
        "cross_project_access": across
    }
    # Obtener el último resultado
    ultimo = get_latest_result()

    if ultimo is None:
        save_results(resultados)
        print("No existe un resultado anterior.")
        return
    resultado_anterior = load_result(ultimo)

    diferencias = compare_results(
        resultado_anterior,
        resultados,
    )

    anomalias = flag_anomalies(diferencias)

    if anomalias:
        print("Anomalías encontradas:")
        for anomalia in anomalias:
            print(f"- {anomalia}")
    else:
        print("No se detectaron anomalías.")
    save_results(resultados)


def main() -> None:
    run_audit_cycle(84000320, 83434201)


if __name__ == "__main__":
    main()

