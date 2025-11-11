import itertools

gensym_counter = itertools.count()

def gensym(prefix="t"):
    """newvar"""
    return f"{prefix}{next(gensym_counter)}"

def normalize_term(m):
    """
    (define normalize-term (lambda (M) (normalize M (lambda (x) x))))
    """
    return normalize(m, lambda x: x)

def is_value(expr):
    """Value?"""
    return (
        isinstance(expr, (int, float, bool, str))
        or expr in ['+', '-', '*', '/', '=']
        or (isinstance(expr, list) and expr and expr[0] == 'lambda')
    )

def normalize_name(m, k):
    """
    (define normalize-name
        (lambda M k)
        (normalize M (lambda (N)
            (if (Value? N) (k N) (let ([t (newvar)]) '(let (,t ,N) ,(k t)))))))
    """
    def cont(n):
        if is_value(n):
            return k(n)
        else:
            t = gensym()
            return ['let', [[t, n]], k(t)]
    return normalize(m, cont)

def normalize_name_star(m_star, k):
    """
    (define normalize-name*
        (lambda (M* k)
            (if (null? M*)
                (k '())
                (normalize-name
                    (car M*) (lambda (t) (normalize-name* (cdr M*) (lambda (t*) (k '(,t . ,t*)))))))))
    """
    if not m_star:
        return k([])
    car, *cdr = m_star
    return normalize_name(car, lambda t:
        normalize_name_star(cdr, lambda t_star:
            k([t] + t_star)))

def normalize(m, k):
    """
    (define normalize
        (lambda (M k))
            (match M
                ['(lambda ,params ,body) (k '(lambda ,params ,(normalize-term body)))]
                ['(let (,x ,M_1), M_2) (normalize M_1 (lambda (N_1) '(let (,x ,N_1) ,(normalize M_2 k))))]
                ['(if0 ,M_1 ,M_2 ,M_3) (normalize-name M_1 (lambda (t) (k '(if0 ,t ,(normalize-term M_2) ,(normalize-term M_3)))))]
                ['(, F_n . ,M*) (if (PrimOp? Fn)
                                    (normalize-name* M* (lambda (t*) (k '(,Fn . ,t*))))
                                    (normalize-name Fn (lambda (t) (normalize-name* M* (lambda (t*) (k '(,t . ,t*)))))))]
                [V (k V)]))
    """
    # lambda
    if isinstance(m, list) and len(m) >= 3 and m[0] == 'lambda':
        params, body = m[1], m[2]
        return k(['lambda', params, normalize_term(body)])

    # let
    elif isinstance(m, list) and len(m) == 3 and m[0] == 'let':
        x, m1 = m[1]
        m2 = m[2]
        return normalize(m1, lambda n1:
            ['let', [[x, n1]], normalize(m2, k)]
        )

    # if
    elif isinstance(m, list) and len(m) == 4 and m[0] == 'if':
        m1, m2, m3 = m[1], m[2], m[3]
        return normalize_name(m1, lambda t: k(['if', t, normalize_term(m2), normalize_term(m3)]))

    elif isinstance(m, list) and len(m) >= 1:
        fn, *m_star = m
        # primitve operation
        if isinstance(fn, str) and fn in ['+', '-', '*', '/', '=', '<', '>']:
            return normalize_name_star(m_star, lambda t_star: k([fn] + t_star))
        # function application
        else:
            return normalize_name(fn, lambda t:
                normalize_name_star(m_star, lambda t_star:
                    k([t] + t_star)
                )
            )

    # atomic value
    elif is_value(m):
        return k(m)

    else:
        raise ValueError(f"unrecognized form: {m}")
