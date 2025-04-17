from mondey_backend.import_data.utils import get_import_current_session

# implements https://github.com/ssciwr/mondey/pull/284/commits/6e240b1ec7a3b364fd2b356767b5abf8bdec59a7


def transform_younger_older_siblings():
    import_session = get_import_current_session()
    with import_session:
        child_ids = [c[0] for c in import_session.execute("select id from child")]
        for child_id in child_ids:
            cur = import_session.cursor()
            for question_id in [17, 18]:
                if not cur.execute(
                    f"select * from childanswer where child_id={child_id} and question_id={question_id}"
                ).fetchone():
                    sql = f"insert into childanswer values (0, NULL, {child_id}, {question_id});"
                    print(sql)
                    cur.execute(sql)
