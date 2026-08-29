/* i18n.js — rule-based multilingual layer for the demonstration fabrics.
 *
 * Honest by construction, matching the product story exactly: the QUERY and
 * the ANSWER are translated; the source documents stay as written (English),
 * and every citation opens the original passage.
 *
 * How it works — no model, no network:
 *   1. Every sentence in every corpus is generated from ~66 sentence
 *      templates (pipeline/docgen.py). This file carries those templates in
 *      French, Spanish and Japanese, with {n} slots. An answer sentence is
 *      matched back to its template with a compiled regex and re-rendered in
 *      the reader's language; slot values (units, roles, systems, section
 *      names, codes) stay as written in the source — labelled, like a real
 *      translation memo. A sentence that matches no template stays quoted in
 *      English with an EN tag (code tables, rare wrap artefacts).
 *   2. Queries in FR/ES/JA are translated to English keywords before
 *      retrieval: a question-vocabulary dictionary per language, a shared
 *      domain glossary, cognate suffix rules for FR/ES, and longest-first
 *      substring matching for Japanese (which has no spaces).
 */
(function (global) {
  "use strict";

  /* ---------------------------------------------------------- UI strings */
  const UI = {
    en: {
      placeholder: "Ask this corpus a question…",
      ask: "Ask", sources: "Sources", confidence: "Confidence",
      suggestLead: "Try:",
      answerIdle: "Ask a question above, or pick one of the suggestions, to populate this section with a cited answer.",
      metaIdle: "Confidence, source count and graph activation appear here.",
      noAnswer: "No grounded answer",
      noAnswerBody: "Nothing in this corpus supports an answer to",
      noAnswerNote: "This is a deliberate non-answer. Assembling a confident-sounding paragraph from loosely related passages is the failure mode this design exists to prevent.",
      whyDegenerate: "That query is made entirely of function words, so there is no retrievable intent in it. Try naming a process, a document type or a standard.",
      whyNoMatch: "Neither the lexical nor the semantic retriever found a passage above threshold. The subject may genuinely not be covered by this corpus.",
      whyNoCoverage: "Passages were retrieved, but none contained a sentence that actually addresses the terms asked about. Quoting one anyway would misrepresent the corpus.",
      translatedNote: "", enTag: "",
    },
    fr: {
      placeholder: "Posez une question à ce corpus…",
      ask: "Demander", sources: "Sources", confidence: "Confiance",
      suggestLead: "Essayez :",
      answerIdle: "Posez une question ci-dessus, ou choisissez une suggestion, pour obtenir une réponse citée.",
      metaIdle: "La confiance, le nombre de sources et l'activation du graphe apparaissent ici.",
      noAnswer: "Pas de réponse fondée",
      noAnswerBody: "Rien dans ce corpus ne permet de répondre à",
      noAnswerNote: "C'est un non-réponse délibéré. Assembler un paragraphe d'apparence sûre à partir de passages vaguement liés est précisément l'échec que cette conception évite.",
      whyDegenerate: "Cette question ne contient que des mots-outils : aucune intention n'est récupérable. Nommez un processus, un type de document ou une norme.",
      whyNoMatch: "Ni la recherche lexicale ni la recherche sémantique n'ont trouvé de passage au-dessus du seuil. Le sujet n'est peut-être réellement pas couvert par ce corpus.",
      whyNoCoverage: "Des passages ont été trouvés, mais aucune phrase ne traite réellement des termes demandés. En citer une quand même trahirait le corpus.",
      translatedNote: "Réponse traduite des sources anglaises — chaque citation ouvre le passage d'origine.",
      enTag: "cité en anglais",
    },
    es: {
      placeholder: "Haga una pregunta a este corpus…",
      ask: "Preguntar", sources: "Fuentes", confidence: "Confianza",
      suggestLead: "Pruebe:",
      answerIdle: "Haga una pregunta arriba, o elija una sugerencia, para obtener una respuesta con citas.",
      metaIdle: "La confianza, el número de fuentes y la activación del grafo aparecen aquí.",
      noAnswer: "Sin respuesta fundamentada",
      noAnswerBody: "Nada en este corpus respalda una respuesta a",
      noAnswerNote: "Es una no-respuesta deliberada. Componer un párrafo de apariencia segura con pasajes vagamente relacionados es exactamente el fallo que este diseño evita.",
      whyDegenerate: "La consulta se compone solo de palabras funcionales: no hay intención recuperable. Nombre un proceso, un tipo de documento o una norma.",
      whyNoMatch: "Ni el buscador léxico ni el semántico encontraron un pasaje por encima del umbral. Puede que el corpus realmente no cubra el tema.",
      whyNoCoverage: "Se recuperaron pasajes, pero ninguna frase aborda realmente los términos preguntados. Citar una de todos modos tergiversaría el corpus.",
      translatedNote: "Respuesta traducida de las fuentes en inglés — cada cita abre el pasaje original.",
      enTag: "citado en inglés",
    },
    ja: {
      placeholder: "このコーパスに質問してください…",
      ask: "質問する", sources: "出典", confidence: "確信度",
      suggestLead: "例：",
      answerIdle: "上の入力欄で質問するか、候補を選ぶと、出典付きの回答が表示されます。",
      metaIdle: "確信度・出典数・グラフの活性化がここに表示されます。",
      noAnswer: "根拠のある回答なし",
      noAnswerBody: "このコーパスには次の質問に答える根拠がありません：",
      noAnswerNote: "これは意図的な「回答しない」判断です。関連の薄い文をつなぎ合わせて自信ありげな段落を作ることこそ、この設計が防いでいる失敗です。",
      whyDegenerate: "この質問は機能語のみで構成されており、検索できる意図がありません。プロセス名・文書種別・規格名を含めてください。",
      whyNoMatch: "語彙検索・意味検索のいずれも、しきい値を超える文書箇所を見つけられませんでした。このコーパスが本当に扱っていない主題かもしれません。",
      whyNoCoverage: "文書箇所は見つかりましたが、質問の語に実際に答える文はありませんでした。それでも引用すればコーパスを誤って伝えることになります。",
      translatedNote: "回答は英語の出典から翻訳されています — 各引用は原文の該当箇所を開きます。",
      enTag: "原文（英語）",
    },
  };

  /* ----------------------------------------------- sentence templates
     [en pattern, fr, es, ja] — slots {} in EN, {1}-based refs elsewhere. */
  const TPL = [
    ["{} for {} is performed by {} and evidenced in {}.",
     "{1} pour {2} est réalisé par {3} et attesté dans {4}.",
     "{1} para {2} lo realiza {3} y queda evidenciado en {4}.",
     "{2}の{1}は{3}が実施し、{4}に記録として残す。"],
    ["This section sets the {} requirements that apply to {} at {}.",
     "Cette section fixe les exigences de {1} applicables à {2} sur le site {3}.",
     "Esta sección establece los requisitos de {1} aplicables a {2} en {3}.",
     "本節は、{3}における{2}に適用される{1}の要求事項を定める。"],
    ["{} confirms that {} has been completed before the item advances beyond '{}'.",
     "{1} confirme que {2} est achevé avant que l'élément ne dépasse l'état « {3} ».",
     "{1} confirma que {2} se ha completado antes de que el elemento avance más allá de «{3}».",
     "{1}は、対象が「{3}」の先へ進む前に{2}が完了していることを確認する。"],
    ["Where {} cannot be completed as specified, the shortfall is recorded against {} and escalated within {} hours.",
     "Lorsque {1} ne peut être réalisé comme prescrit, l'écart est enregistré au titre de {2} et escaladé sous {3} heures.",
     "Cuando {1} no puede completarse según lo especificado, la desviación se registra contra {2} y se escala en un plazo de {3} horas.",
     "{1}を規定どおり完了できない場合、その不足は{2}に対して記録し、{3}時間以内にエスカレーションする。"],
    ["{} is assessed against {} and against the {} requirements held by {}.",
     "{1} est évalué au regard de {2} et des exigences {3} détenues par {4}.",
     "{1} se evalúa frente a {2} y frente a los requisitos de {3} que mantiene {4}.",
     "{1}は、{2}および{4}が保有する{3}の要求事項に照らして評価する。"],
    ["This document establishes how {} governs {} across {} operations, and supersedes any local practice that conflicts with it.",
     "Ce document établit comment {1} gouverne {2} dans l'ensemble des opérations {3}, et prévaut sur toute pratique locale contraire.",
     "Este documento establece cómo {1} gobierna {2} en las operaciones de {3}, y prevalece sobre cualquier práctica local que lo contradiga.",
     "本書は、{3}の業務全体において{1}が{2}をどのように統制するかを定め、これに反するローカルな慣行に優先する。"],
    ["The scope covers {} from initiation through to '{}', including work performed at {} and by delegated third parties acting on behalf of {}.",
     "Le périmètre couvre {1} de l'initiation jusqu'à « {2} », y compris les travaux réalisés sur {3} et par des tiers délégués agissant pour {4}.",
     "El alcance cubre {1} desde el inicio hasta «{2}», incluido el trabajo realizado en {3} y por terceros delegados en nombre de {4}.",
     "適用範囲は、開始から「{2}」までの{1}を対象とし、{3}での作業および{4}の委任を受けた第三者の作業を含む。"],
    ["Requirements derive from {}; where that authority is silent, the more restrictive of local practice and this document applies.",
     "Les exigences découlent de {1} ; lorsque cette autorité est muette, la plus restrictive entre la pratique locale et ce document s'applique.",
     "Los requisitos derivan de {1}; cuando esa autoridad guarda silencio, se aplica la más restrictiva entre la práctica local y este documento.",
     "要求事項は{1}に由来する。当該規範に定めのない事項については、ローカルな慣行と本書のうち、より厳格な方を適用する。"],
    ["Out of scope: activities managed under a separate authority, and any {} performed outside {}'s certificate or contractual remit.",
     "Hors périmètre : les activités gérées sous une autorité distincte, et tout {1} réalisé hors du certificat ou du mandat contractuel de {2}.",
     "Fuera de alcance: actividades gestionadas bajo otra autoridad, y todo {1} realizado fuera del certificado o del mandato contractual de {2}.",
     "適用範囲外：別の規範の下で管理される活動、および{2}の認可・契約範囲の外で行われる{1}。"],
    ["The intent is to make {} reconstructable after the fact.",
     "L'intention est de rendre {1} reconstituable a posteriori.",
     "La intención es que {1} sea reconstruible a posteriori.",
     "意図は、{1}を事後に再構成できるようにすることである。"],
    ["A reviewer who was not present must be able to reach the same conclusion from the record alone.",
     "Un examinateur absent des faits doit pouvoir atteindre la même conclusion à partir du seul enregistrement.",
     "Un revisor que no estuvo presente debe poder llegar a la misma conclusión solo a partir del registro.",
     "その場にいなかった審査者が、記録だけから同じ結論に到達できなければならない。"],
    ["This applies to all personnel in {} and to any contracted resource performing {} at {}.",
     "Ceci s'applique à tout le personnel de {1} et à toute ressource sous-traitée réalisant {2} sur {3}.",
     "Esto aplica a todo el personal de {1} y a cualquier recurso contratado que realice {2} en {3}.",
     "本規定は、{1}の全要員、および{3}で{2}を行う契約要員に適用される。"],
    ["Applicability is determined by configuration and effectivity, not by convenience of scheduling; where effectivity is ambiguous, {} makes the determination and records the basis.",
     "L'applicabilité est déterminée par la configuration et l'effectivité, non par la commodité du planning ; en cas d'ambiguïté, {1} tranche et consigne le fondement.",
     "La aplicabilidad se determina por configuración y efectividad, no por conveniencia de programación; ante ambigüedad, {1} decide y registra el fundamento.",
     "適用可否は構成と有効性によって決まり、日程の都合では決まらない。有効性が不明確な場合は{1}が判断し、その根拠を記録する。"],
    ["Items entering the process in state '{}' are in scope.",
     "Les éléments entrant dans le processus à l'état « {1} » sont dans le périmètre.",
     "Los elementos que entran al proceso en estado «{1}» están en alcance.",
     "「{1}」の状態でプロセスに入る対象は適用範囲内である。"],
    ["Items already past '{}' are handled under the change process instead.",
     "Les éléments ayant déjà dépassé « {1} » relèvent du processus de modification.",
     "Los elementos que ya superaron «{1}» se gestionan por el proceso de cambios.",
     "既に「{1}」を過ぎた対象は、代わりに変更管理プロセスで扱う。"],
    ["Where {} applies, the more specific classification takes precedence over the general category.",
     "Lorsque {1} s'applique, la classification la plus spécifique prévaut sur la catégorie générale.",
     "Cuando aplica {1}, la clasificación más específica prevalece sobre la categoría general.",
     "{1}が適用される場合、より具体的な分類が一般分類に優先する。"],
    ["Exclusions must be documented at the point of decision.",
     "Les exclusions doivent être documentées au moment de la décision.",
     "Las exclusiones deben documentarse en el momento de la decisión.",
     "適用除外は、判断した時点で文書化しなければならない。"],
    ["An undocumented exclusion is treated as an unassessed item.",
     "Une exclusion non documentée est traitée comme un élément non évalué.",
     "Una exclusión no documentada se trata como un elemento no evaluado.",
     "文書化されていない適用除外は、未評価の対象として扱う。"],
    ["Acceptance requires all mandatory checks to pass with no open findings above the agreed threshold, verified within {} hours of completion.",
     "L'acceptation exige la réussite de tous les contrôles obligatoires, sans constat ouvert au-dessus du seuil convenu, vérifiée sous {1} heures après achèvement.",
     "La aceptación exige aprobar todos los controles obligatorios sin hallazgos abiertos por encima del umbral acordado, verificado en {1} horas tras la finalización.",
     "受入れには、合意したしきい値を超える未解決の指摘なく全必須チェックに合格し、完了後{1}時間以内に検証されることを要する。"],
    ["The tolerance band is fixed at issue and may not be widened during execution; a widening requires a new revision approved by {}.",
     "La bande de tolérance est fixée à l'émission et ne peut être élargie en cours d'exécution ; tout élargissement exige une nouvelle révision approuvée par {1}.",
     "La banda de tolerancia se fija en la emisión y no puede ampliarse durante la ejecución; ampliarla exige una nueva revisión aprobada por {1}.",
     "許容範囲は発行時に確定し、実施中に広げてはならない。拡大には{1}が承認する新しい改訂を要する。"],
    ["Where measurement is subjective, at least {} independent observations are required before a conclusion is recorded.",
     "Lorsque la mesure est subjective, au moins {1} observations indépendantes sont requises avant d'enregistrer une conclusion.",
     "Cuando la medición es subjetiva, se requieren al menos {1} observaciones independientes antes de registrar una conclusión.",
     "測定が主観的な場合、結論を記録する前に少なくとも{1}回の独立した観察を要する。"],
    ["Performance is considered acceptable at {}% or above against the stated measure, assessed on a rolling {}-day window rather than a single observation.",
     "La performance est jugée acceptable à partir de {1} % au regard de la mesure énoncée, évaluée sur une fenêtre glissante de {2} jours plutôt que sur une observation unique.",
     "El desempeño se considera aceptable a partir del {1} % frente a la medida indicada, evaluado en una ventana móvil de {2} días y no en una única observación.",
     "性能は、単発の観測ではなく{2}日間のローリング窓で評価し、規定の指標に対して{1}%以上で許容とみなす。"],
    ["Criteria referencing {} are restated in full here so the reader does not have to hold two documents open to apply them.",
     "Les critères faisant référence à {1} sont repris ici en intégralité, afin que le lecteur n'ait pas à tenir deux documents ouverts pour les appliquer.",
     "Los criterios que remiten a {1} se reproducen aquí íntegramente para que el lector no tenga que mantener dos documentos abiertos al aplicarlos.",
     "{1}を参照する基準は、適用時に二つの文書を並べて参照せずに済むよう、ここに全文を再掲する。"],
    ["A borderline result is not a pass.",
     "Un résultat limite n'est pas une réussite.",
     "Un resultado en el límite no es un aprobado.",
     "境界線上の結果は合格ではない。"],
    ["If the outcome sits within measurement uncertainty of the limit, it is escalated to {} for adjudication.",
     "Si le résultat se situe dans l'incertitude de mesure de la limite, il est escaladé à {1} pour arbitrage.",
     "Si el resultado queda dentro de la incertidumbre de medición del límite, se escala a {1} para su adjudicación.",
     "結果が限界値の測定不確かさの範囲内にある場合は、{1}へエスカレーションして裁定を仰ぐ。"],
    ["Confirm the item is in state '{}' and that prerequisites are complete before starting; starting out of sequence invalidates the downstream verification.",
     "Confirmer que l'élément est à l'état « {1} » et que les prérequis sont remplis avant de commencer ; démarrer hors séquence invalide la vérification aval.",
     "Confirme que el elemento está en estado «{1}» y que los prerrequisitos están completos antes de empezar; iniciar fuera de secuencia invalida la verificación posterior.",
     "開始前に、対象が「{1}」の状態であり前提条件が完了していることを確認する。順序を外れた着手は後段の検証を無効にする。"],
    ["Record each step in {} as it is completed rather than retrospectively at the end of the task.",
     "Enregistrer chaque étape dans {1} au fil de l'exécution, et non rétrospectivement en fin de tâche.",
     "Registre cada paso en {1} a medida que se completa, no retrospectivamente al final de la tarea.",
     "各ステップは、作業終了後にまとめてではなく、完了の都度{1}に記録する。"],
    ["Where the procedure calls for {}, use the current revision only.",
     "Lorsque la procédure requiert {1}, utiliser uniquement la révision en vigueur.",
     "Cuando el procedimiento requiera {1}, use únicamente la revisión vigente.",
     "手順が{1}を求める場合は、最新の有効な改訂のみを使用する。"],
    ["Working from a cached or printed copy is not permitted once a newer revision is effective.",
     "Travailler à partir d'une copie en cache ou imprimée n'est pas autorisé dès qu'une révision plus récente est en vigueur.",
     "No se permite trabajar con una copia en caché o impresa una vez que una revisión más reciente está en vigor.",
     "新しい改訂が有効になった後は、キャッシュや印刷済みの写しで作業してはならない。"],
    ["On completion, hand the item to {} for independent check.",
     "À l'achèvement, remettre l'élément à {1} pour contrôle indépendant.",
     "Al finalizar, entregue el elemento a {1} para una verificación independiente.",
     "完了時には、対象を{1}に引き渡して独立したチェックを受ける。"],
    ["The person who performed the work may not also verify it.",
     "La personne qui a réalisé le travail ne peut pas aussi le vérifier.",
     "La persona que realizó el trabajo no puede también verificarlo.",
     "作業を実施した本人が、その検証を兼ねてはならない。"],
    ["If the condition found differs from the condition expected, stop and raise the deviation before proceeding — do not adapt the procedure in place.",
     "Si l'état constaté diffère de l'état attendu, s'arrêter et déclarer l'écart avant de poursuivre — ne pas adapter la procédure sur place.",
     "Si la condición hallada difiere de la esperada, deténgase y levante la desviación antes de continuar — no adapte el procedimiento sobre la marcha.",
     "発見した状態が想定と異なる場合は、作業を止め、進める前に逸脱を起票する。手順をその場で改変してはならない。"],
    ["Interruptions longer than {} hours require the prerequisite checks to be repeated before work resumes.",
     "Toute interruption de plus de {1} heures impose de répéter les vérifications préalables avant la reprise.",
     "Las interrupciones de más de {1} horas exigen repetir las verificaciones previas antes de reanudar.",
     "{1}時間を超える中断の後は、作業再開前に前提チェックを再実施する。"],
    ["Assessment considers likelihood and consequence together; a low-likelihood outcome with severe consequence is not downgraded on frequency alone.",
     "L'évaluation considère ensemble vraisemblance et conséquence ; un événement peu probable aux conséquences graves n'est pas déclassé sur la seule fréquence.",
     "La evaluación considera probabilidad y consecuencia en conjunto; un resultado poco probable con consecuencias graves no se degrada solo por frecuencia.",
     "評価は発生可能性と影響度を併せて行う。発生確率が低くとも影響が重大な事象を、頻度だけで格下げしてはならない。"],
    ["The analysis must identify what would have to be true for the conclusion to be wrong, and state whether that condition was tested or assumed.",
     "L'analyse doit identifier ce qui devrait être vrai pour que la conclusion soit fausse, et préciser si cette condition a été testée ou supposée.",
     "El análisis debe identificar qué tendría que ser cierto para que la conclusión fuera errónea, y declarar si esa condición se probó o se asumió.",
     "分析では、結論が誤りとなるために何が真でなければならないかを特定し、その条件を検証したのか仮定したのかを明示する。"],
    ["Contributing factors are recorded separately from the immediate cause.",
     "Les facteurs contributifs sont enregistrés séparément de la cause immédiate.",
     "Los factores contribuyentes se registran por separado de la causa inmediata.",
     "寄与要因は直接原因とは分けて記録する。"],
    ["Recording only the immediate cause produces corrective actions that do not prevent recurrence.",
     "N'enregistrer que la cause immédiate produit des actions correctives qui n'empêchent pas la récurrence.",
     "Registrar solo la causa inmediata produce acciones correctivas que no evitan la recurrencia.",
     "直接原因のみを記録すると、再発を防げない是正処置になる。"],
    ["Where {} interacts with adjacent processes, the assessment extends to those interfaces rather than stopping at the {} boundary.",
     "Lorsque {1} interagit avec des processus adjacents, l'évaluation s'étend à ces interfaces au lieu de s'arrêter à la frontière de {2}.",
     "Cuando {1} interactúa con procesos adyacentes, la evaluación se extiende a esas interfaces en lugar de detenerse en el límite de {2}.",
     "{1}が隣接プロセスと相互作用する場合、評価は{2}の境界で止めず、それらの接点まで広げる。"],
    ["Quantitative inputs are traced to their source system.",
     "Les données quantitatives sont tracées jusqu'à leur système source.",
     "Los datos cuantitativos se trazan hasta su sistema de origen.",
     "定量的な入力は、その発生元システムまで追跡する。"],
    ["An input that cannot be traced is treated as an assumption and declared as such.",
     "Une donnée introuvable à la source est traitée comme une hypothèse et déclarée comme telle.",
     "Un dato que no puede trazarse se trata como un supuesto y se declara como tal.",
     "追跡できない入力は仮定として扱い、その旨を明示する。"],
    ["{} reviews the assessment for proportionality: over-assessment consumes capacity that a genuinely higher risk elsewhere needs.",
     "{1} revoit l'évaluation sous l'angle de la proportionnalité : sur-évaluer consomme une capacité dont un risque réellement plus élevé a besoin ailleurs.",
     "{1} revisa la evaluación por proporcionalidad: sobre-evaluar consume capacidad que un riesgo realmente mayor necesita en otra parte.",
     "{1}は評価の妥当な釣り合いを審査する。過剰な評価は、他所の本当に高いリスクが必要とする対応力を消費する。"],
    ["Records are created contemporaneously, attributable to a named individual, legible, original and accurate.",
     "Les enregistrements sont créés au moment des faits, attribuables à une personne nommée, lisibles, originaux et exacts.",
     "Los registros se crean en el momento, son atribuibles a una persona identificada, legibles, originales y exactos.",
     "記録は同時性をもって作成し、特定の個人に帰属でき、判読可能で、原本であり、正確でなければならない。"],
    ["Each entry carries the identifier of the item, the date, the performing individual and the outcome.",
     "Chaque entrée porte l'identifiant de l'élément, la date, l'exécutant et le résultat.",
     "Cada entrada lleva el identificador del elemento, la fecha, la persona ejecutante y el resultado.",
     "各記入項目には、対象の識別子・日付・実施者・結果を記載する。"],
    ["Entries missing any of these are incomplete regardless of the work performed.",
     "Une entrée à laquelle il manque l'un de ces éléments est incomplète, quel que soit le travail réalisé.",
     "Las entradas que carecen de cualquiera de estos elementos son incompletas, independientemente del trabajo realizado.",
     "これらのいずれかを欠く記入は、実施した作業の如何にかかわらず不完全である。"],
    ["Corrections are made by single strike-through with initials and date; the original entry must remain readable.",
     "Les corrections se font par simple rature avec initiales et date ; l'entrée d'origine doit rester lisible.",
     "Las correcciones se hacen con una sola línea de tachado, iniciales y fecha; la entrada original debe permanecer legible.",
     "訂正は一本線の抹消にイニシャルと日付を添えて行い、元の記載が読めるまま残らなければならない。"],
    ["Obliteration is a data integrity finding.",
     "L'oblitération constitue un constat d'intégrité des données.",
     "La obliteración constituye un hallazgo de integridad de datos.",
     "塗りつぶしはデータインテグリティ上の指摘事項となる。"],
    ["Electronic records in {} carry an audit trail that cannot be disabled by the record's author.",
     "Les enregistrements électroniques dans {1} portent une piste d'audit que l'auteur de l'enregistrement ne peut pas désactiver.",
     "Los registros electrónicos en {1} llevan una pista de auditoría que el autor del registro no puede desactivar.",
     "{1}の電子記録には、記録の作成者が無効化できない監査証跡が付随する。"],
    ["Retention runs from the date the record becomes inactive, not from the date it was created.",
     "La conservation court à partir de la date où l'enregistrement devient inactif, non de sa date de création.",
     "La retención corre desde la fecha en que el registro queda inactivo, no desde su creación.",
     "保存期間は、記録が作成された日ではなく、非アクティブになった日から起算する。"],
    ["The evidence set must be sufficient for {} to reach the same conclusion without interviewing the originator.",
     "Le dossier de preuves doit suffire à {1} pour atteindre la même conclusion sans interroger l'auteur.",
     "El conjunto de evidencias debe bastar para que {1} llegue a la misma conclusión sin entrevistar al originador.",
     "証拠一式は、{1}が作成者に聞き取りをせずに同じ結論へ到達できる程度に十分でなければならない。"],
    ["Report within {} hours of discovery.",
     "Déclarer sous {1} heures après la découverte.",
     "Informe dentro de las {1} horas siguientes al descubrimiento.",
     "発見から{1}時間以内に報告する。"],
    ["The reporting clock starts at discovery, not at confirmation.",
     "Le délai de déclaration court dès la découverte, non à la confirmation.",
     "El plazo de reporte empieza en el descubrimiento, no en la confirmación.",
     "報告の起算点は発見時であり、確認時ではない。"],
    ["Escalation to {} is mandatory where the condition affects more than one item, one site, or one period.",
     "L'escalade vers {1} est obligatoire lorsque la condition touche plus d'un élément, d'un site ou d'une période.",
     "La escalada a {1} es obligatoria cuando la condición afecta a más de un elemento, un sitio o un periodo.",
     "事象が複数の対象・拠点・期間に及ぶ場合、{1}へのエスカレーションを必須とする。"],
    ["Interim reports are issued at {}-day intervals until the item reaches '{}'.",
     "Des rapports intermédiaires sont émis tous les {1} jours jusqu'à ce que l'élément atteigne « {2} ».",
     "Se emiten informes provisionales cada {1} días hasta que el elemento alcanza «{2}».",
     "対象が「{2}」に達するまで、{1}日ごとに中間報告を発行する。"],
    ["Communication to affected parties states what is known, what is not yet known, and when the next update will arrive.",
     "La communication aux parties concernées précise ce qui est connu, ce qui ne l'est pas encore, et quand arrivera la prochaine mise à jour.",
     "La comunicación a las partes afectadas indica lo que se sabe, lo que aún no se sabe y cuándo llegará la próxima actualización.",
     "関係者への連絡では、判明している事項・未判明の事項・次回更新の時期を明示する。"],
    ["Under-reporting is treated more seriously than over-reporting: a report later found to be unnecessary carries no sanction.",
     "La sous-déclaration est traitée plus sévèrement que la sur-déclaration : une déclaration jugée ensuite inutile n'entraîne aucune sanction.",
     "No reportar se trata con más severidad que reportar de más: un informe que luego resulta innecesario no conlleva sanción.",
     "過少報告は過剰報告より重大に扱う。後に不要と判明した報告に不利益はない。"],
    ["Closure requires evidence that the action worked, not evidence that the action was taken.",
     "La clôture exige la preuve que l'action a fonctionné, pas la preuve qu'elle a été menée.",
     "El cierre exige evidencia de que la acción funcionó, no de que la acción se realizó.",
     "クローズには、処置を実施した証拠ではなく、処置が効いた証拠を要する。"],
    ["{} is accountable for this document and for the competence of personnel applying it within {}.",
     "{1} est responsable de ce document et de la compétence du personnel qui l'applique au sein de {2}.",
     "{1} es responsable de este documento y de la competencia del personal que lo aplica dentro de {2}.",
     "{1}は本書、および{2}内で本書を適用する要員の力量について説明責任を負う。"],
    ["Approval authority may not be delegated below the level stated here.",
     "L'autorité d'approbation ne peut être déléguée en dessous du niveau indiqué ici.",
     "La autoridad de aprobación no puede delegarse por debajo del nivel aquí indicado.",
     "承認権限を、ここに定める職位より下位へ委任してはならない。"],
    ["Delegation for a defined absence must be recorded in advance.",
     "Une délégation pour absence définie doit être enregistrée à l'avance.",
     "La delegación por una ausencia definida debe registrarse por adelantado.",
     "定められた不在に伴う委任は、事前に記録しなければならない。"],
    ["Compliance is monitored through periodic sampling rather than full census; the sample is drawn at least every {} days and is not selected by the assessed party.",
     "La conformité est surveillée par échantillonnage périodique plutôt que par recensement complet ; l'échantillon est tiré au moins tous les {1} jours et n'est pas choisi par la partie évaluée.",
     "El cumplimiento se supervisa mediante muestreo periódico y no por censo completo; la muestra se extrae al menos cada {1} días y no la elige la parte evaluada.",
     "遵守状況は全数調査ではなく定期的なサンプリングで監視する。サンプルは少なくとも{1}日ごとに抽出し、被評価側は選定に関与しない。"],
    ["Findings are tracked to closure with a named owner and a target date.",
     "Les constats sont suivis jusqu'à clôture avec un responsable nommé et une date cible.",
     "Los hallazgos se siguen hasta el cierre con un responsable designado y una fecha objetivo.",
     "指摘事項は、担当者名と目標期日を付してクローズまで追跡する。"],
    ["A finding without both is not a finding, it is an observation.",
     "Un constat sans ces deux éléments n'est pas un constat, c'est une observation.",
     "Un hallazgo sin ambos no es un hallazgo, es una observación.",
     "その両方を欠くものは指摘事項ではなく、所見にすぎない。"],
    ["This document is reviewed on change of {}, on organisational change affecting {}, and on schedule — whichever falls first.",
     "Ce document est revu à tout changement de {1}, à tout changement organisationnel affectant {2}, et à échéance planifiée — au premier des trois.",
     "Este documento se revisa ante cambios de {1}, ante cambios organizativos que afecten a {2}, y según calendario — lo que ocurra primero.",
     "本書は、{1}の変更時、{2}に影響する組織変更時、および定期時期のいずれか早い時点で見直す。"],
    ["Independence is preserved: verification is performed by someone outside the reporting line that produced the work.",
     "L'indépendance est préservée : la vérification est réalisée par une personne extérieure à la ligne hiérarchique qui a produit le travail.",
     "Se preserva la independencia: la verificación la realiza alguien ajeno a la línea jerárquica que produjo el trabajo.",
     "独立性を保つため、検証は作業を生み出した指揮系統の外の者が実施する。"],
    ["{} references {}, which governs how {} is classified in {}.",
     "{1} fait référence à {2}, qui régit la classification de {3} dans {4}.",
     "{1} remite a {2}, que rige cómo se clasifica {3} en {4}.",
     "{1}は{2}を参照する。{2}は{4}における{3}の分類方法を規定する。"],
    ["Records of {} carry {} so that {} can be reconciled across {} reporting.",
     "Les enregistrements de {1} portent {2}, afin que {3} puisse être rapproché dans les rapports de {4}.",
     "Los registros de {1} llevan {2} para que {3} pueda conciliarse en los informes de {4}.",
     "{1}の記録には{2}を付与し、{4}の報告全体で{3}を突合できるようにする。"],
  ];

  const LANG_I = { fr: 1, es: 2, ja: 3 };

  /* compile EN patterns once */
  const COMPILED = TPL.map(row => {
    const esc = row[0].replace(/[.*+?^${}()|[\]\\]/g, m => m === "{" || m === "}" ? m : "\\" + m);
    return { re: new RegExp("^" + esc.replace(/\{\}/g, "(.+?)") + "$"), row };
  });

  function translateSentence(text, lang) {
    const i = LANG_I[lang];
    if (!i) return null;
    /* the corpus wraps long words as "over- reporting"; templates never do */
    const norm = String(text).trim().replace(/(\S)- (\S)/g, "$1-$2");
    for (const { re, row } of COMPILED) {
      const m = norm.match(re);
      if (m) {
        return row[i].replace(/\{(\d+)\}/g, (_, n) => m[+n] || "");
      }
    }
    return null;
  }

  /* ---------------------------------------------------- query translation */
  /* Question vocabulary + shared domain glossary, per language → English.
     FR/ES entries are lowercase, accent-stripped keys. JA keys are matched
     longest-first as substrings (Japanese has no spaces). */
  const STRIP = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "");
  

  const D_FR = {
    "quel": "which", "quelle": "which", "quels": "which", "quelles": "which",
    "comment": "how", "quand": "when", "pourquoi": "why", "quoi": "what", "qui": "who",
    "declenche": "triggers", "exige": "requires", "exigent": "require", "requiert": "requires",
    "faut": "required", "necessaire": "required", "obligatoire": "mandatory",
    "approbation": "approval", "approuve": "approved", "valide": "approved",
    "suivi": "tracking tracked", "suivis": "tracked", "suivies": "tracked",
    "cloture": "closure", "clos": "closed", "fermeture": "closure",
    "signalement": "reporting", "declaration": "reporting", "declarer": "report",
    "escalade": "escalation", "remontee": "escalation",
    "seuil": "threshold", "delai": "interval hours", "delais": "intervals",
    "enregistrement": "record", "enregistrements": "records", "dossier": "record",
    "preuve": "evidence", "preuves": "evidence", "conservation": "retention",
    "verification": "verification", "controle": "check", "controles": "checks",
    "examen": "review", "revue": "review", "surveillance": "monitoring",
    "echantillonnage": "sampling", "constat": "finding", "constats": "findings",
    "ecart": "deviation", "ecarts": "deviations", "derogation": "waiver",
    "formation": "training", "competence": "competence", "habilitation": "qualification",
    "fournisseur": "vendor supplier", "fournisseurs": "vendors",
    "reclamation": "complaint", "reclamations": "complaints", "plainte": "complaint",
    "enquete": "investigation", "cause": "cause", "recidive": "recurrence",
    "lot": "batch", "sterilite": "sterility", "etalonnage": "calibration",
    "maintenance": "maintenance", "entretien": "maintenance", "revision": "revision overhaul",
    "navigabilite": "airworthiness", "consigne": "directive", "inspection": "inspection",
    "securite": "safety security", "surete": "security", "exercice": "drill",
    "rassemblement": "muster", "sinistre": "claim", "indemnisation": "claim settlement",
    "refus": "denial", "police": "policy", "polices": "policies",
    "garantie": "covenant warranty", "garanties": "covenants",
    "notation": "rating", "credit": "credit", "comite": "committee",
    "blanchiment": "laundering aml", "vigilance": "due diligence", "diligence": "diligence", "renforcee": "enhanced",
    "liquidites": "cash", "especes": "cash", "entreprise": "business", "entreprises": "business",
    "alerte": "alert", "alertes": "alerts", "structuration": "structuring",
    "modele": "model", "modeles": "models", "validation": "validation",
    "risque": "risk", "risques": "risks", "conformite": "compliance",
    "audit": "audit", "audits": "audits", "tracabilite": "traceability lineage",
    "exigence": "requirement", "exigences": "requirements", "norme": "standard",
    "procedure": "procedure", "procedures": "procedures", "processus": "process",
    "defaut": "defect", "defauts": "defects", "anomalie": "defect finding",
    "essai": "test", "essais": "tests", "cas": "case",
    "version": "version revision", "perime": "superseded", "obsolete": "superseded",
    "chaine": "chain", "froid": "cold", "peremption": "expiry", "rappel": "recall",
    "etiquetage": "labelling", "stock": "inventory", "entrepot": "warehouse",
    "hygiene": "sanitation", "assainissement": "sanitation", "passerelle": "gangway",
    "specification": "specification", "specifications": "specifications",
  };

  const D_ES = {
    "que": "what", "cual": "which", "cuales": "which", "como": "how",
    "cuando": "when", "quien": "who", "donde": "where", "por": "", "para": "",
    "desencadena": "triggers", "activa": "triggers", "exige": "requires",
    "requiere": "requires", "requieren": "require", "necesario": "required",
    "obligatorio": "mandatory", "obligatoria": "mandatory",
    "aprobacion": "approval", "aprobado": "approved", "aprueba": "approves",
    "seguimiento": "tracking tracked", "rastrea": "tracked", "rastrean": "tracked",
    "cierre": "closure", "cerrado": "closed", "clausura": "closure",
    "reporte": "reporting", "informe": "report", "informes": "reports",
    "notificacion": "reporting", "escalado": "escalation", "escalamiento": "escalation",
    "umbral": "threshold", "plazo": "interval hours", "plazos": "intervals",
    "registro": "record", "registros": "records", "expediente": "record",
    "evidencia": "evidence", "evidencias": "evidence", "retencion": "retention",
    "verificacion": "verification", "control": "check", "controles": "checks",
    "revision": "review revision", "vigilancia": "monitoring", "monitoreo": "monitoring",
    "muestreo": "sampling", "hallazgo": "finding", "hallazgos": "findings",
    "desviacion": "deviation", "desviaciones": "deviations",
    "capacitacion": "training", "formacion": "training", "competencia": "competence",
    "proveedor": "vendor supplier", "proveedores": "vendors",
    "queja": "complaint", "quejas": "complaints", "reclamacion": "complaint claim",
    "investigacion": "investigation", "causa": "cause", "recurrencia": "recurrence",
    "lote": "batch", "esterilidad": "sterility", "calibracion": "calibration",
    "mantenimiento": "maintenance", "aeronavegabilidad": "airworthiness",
    "directiva": "directive", "inspeccion": "inspection",
    "seguridad": "safety security", "simulacro": "drill", "reunion": "muster",
    "siniestro": "claim", "denegacion": "denial", "poliza": "policy", "polizas": "policies",
    "pacto": "covenant", "pactos": "covenants", "clausula": "covenant clause",
    "calificacion": "rating", "credito": "credit", "comite": "committee",
    "lavado": "laundering aml", "debida": "due", "diligencia": "diligence", "reforzada": "enhanced",
    "efectivo": "cash", "empresa": "business", "empresas": "business", "negocio": "business",
    "alerta": "alert", "alertas": "alerts", "estructuracion": "structuring",
    "modelo": "model", "modelos": "models", "validacion": "validation",
    "riesgo": "risk", "riesgos": "risks", "cumplimiento": "compliance",
    "auditoria": "audit", "trazabilidad": "traceability lineage",
    "requisito": "requirement", "requisitos": "requirements", "norma": "standard",
    "procedimiento": "procedure", "procedimientos": "procedures", "proceso": "process",
    "defecto": "defect", "defectos": "defects", "prueba": "test", "pruebas": "tests",
    "caso": "case", "version": "version revision", "obsoleto": "superseded",
    "cadena": "chain", "frio": "cold", "caducidad": "expiry", "retiro": "recall",
    "etiquetado": "labelling", "inventario": "inventory", "almacen": "warehouse",
    "saneamiento": "sanitation", "higiene": "sanitation",
    "especificacion": "specification", "especificaciones": "specifications",
  };

  /* Japanese: longest-first substring dictionary. */
  const D_JA = {
    "デューデリジェンス": "due diligence", "厳格な顧客管理": "enhanced due diligence",
    "マネーロンダリング": "laundering aml", "疑わしい取引": "suspicious transaction structuring",
    "取引モニタリング": "transaction monitoring", "ストラクチャリング": "structuring",
    "信用格付": "credit risk rating", "格付": "rating", "与信委員会": "credit committee",
    "委員会": "committee", "承認": "approval", "権限": "authority delegated",
    "コベナンツ": "covenants", "特約": "covenant", "融資": "facility loan",
    "商業用不動産": "commercial real estate", "モデル検証": "model validation",
    "モデル": "model", "検証": "validation verification", "指摘事項": "findings",
    "指摘": "finding", "是正処置": "corrective action capa", "逸脱": "deviation",
    "クレーム": "complaint claim", "苦情": "complaint", "調査": "investigation",
    "報告": "report reporting", "通報": "reporting", "エスカレーション": "escalation",
    "しきい値": "threshold", "閾値": "threshold", "監査証跡": "audit trail",
    "監査": "audit", "追跡": "tracked traceability", "クローズ": "closure",
    "完了": "closure completed", "記録": "records", "証拠": "evidence",
    "保存期間": "retention", "保管": "retention", "校正": "calibration",
    "滅菌": "sterility", "無菌": "sterility", "バッチ": "batch", "ロット": "batch",
    "整備": "maintenance", "耐空性": "airworthiness", "耐空性改善命令": "airworthiness directive",
    "点検": "inspection check", "検査": "inspection", "訓練": "training drill",
    "避難訓練": "muster drill", "安全": "safety", "セキュリティ": "security",
    "サプライヤー": "supplier vendor", "ベンダー": "vendor", "仕入先": "vendor",
    "仕様": "specification", "仕様書": "specification", "要求事項": "requirements",
    "要件": "requirements", "規格": "standard", "手順": "procedure",
    "手順書": "procedure", "プロセス": "process", "文書": "document",
    "改訂": "revision", "版": "revision version", "旧版": "superseded",
    "廃止": "superseded", "有効": "effective current", "コールドチェーン": "cold chain",
    "有効期限": "expiry", "リコール": "recall", "回収": "recall",
    "ラベル": "labelling label", "表示": "labelling", "在庫": "inventory",
    "倉庫": "warehouse", "衛生": "sanitation", "サニテーション": "sanitation",
    "リスク": "risk", "コンプライアンス": "compliance", "遵守": "compliance",
    "保険金請求": "claim", "保険金": "claim", "支払拒否": "denial", "否認": "denial",
    "保険契約": "policy", "約款": "policy wording", "テストケース": "test case",
    "テスト": "test", "不具合": "defect", "欠陥": "defect", "バグ": "defect",
    "トリガー": "triggers", "必要": "required", "必須": "mandatory",
    "何が": "what", "何を": "what", "どの": "which", "どのように": "how",
    "どうやって": "how", "いつ": "when", "誰が": "who", "なぜ": "why",
    "現金集約型事業": "cash-intensive business", "現金": "cash",
  };
  const JA_KEYS = Object.keys(D_JA).sort((a, b) => b.length - a.length);

  function detect(q) {
    const s = String(q);
    if (/[\u3040-\u30FF\u4E00-\u9FFF]/.test(s)) return "ja";
    const low = " " + STRIP(s.toLowerCase()) + " ";
    let fr = 0, es = 0;
    for (const w of [" quel", " quelle", " comment ", " les ", " des ", " est ", " sont ", " une ", " qui ", " quand "])
      if (low.includes(w)) fr++;
    for (const w of [" que ", " cual", " como ", " los ", " las ", " es ", " son ", " una ", " cuando ", " para "])
      if (low.includes(w)) es++;
    if (/[¿¡]|ñ/.test(s)) es += 2;
    if (/[àâçèêëîïôùû]|œ/.test(s)) fr += 2;
    if (fr === 0 && es === 0) return "en";
    return fr >= es ? "fr" : "es";
  }

  function cognate(tok, lang) {
    /* accent-stripped token → English-ish via suffix rules; pass through if
       already plausible English (many domain terms are shared). */
    let t = tok;
    if (lang === "es") {
      t = t.replace(/cion$/, "tion").replace(/ciones$/, "tions")
           .replace(/dad$/, "ty").replace(/mente$/, "ly")
           .replace(/ico$/, "ic").replace(/ica$/, "ic");
    } else if (lang === "fr") {
      t = t.replace(/ique$/, "ic").replace(/iques$/, "ics")
           .replace(/ement$/, "ement").replace(/eur$/, "or");
    }
    return t;
  }

  function toEnglish(q, lang) {
    if (lang === "ja") {
      let rest = String(q);
      const out = [];
      let moved = true;
      while (moved) {
        moved = false;
        for (const k of JA_KEYS) {
          const i = rest.indexOf(k);
          if (i >= 0) { out.push(D_JA[k]); rest = rest.slice(0, i) + " " + rest.slice(i + k.length); moved = true; break; }
        }
      }
      const ascii = rest.match(/[A-Za-z][A-Za-z0-9-]+/g) || [];
      return (out.join(" ") + " " + ascii.join(" ")).trim();
    }
    const dict = lang === "fr" ? D_FR : lang === "es" ? D_ES : null;
    if (!dict) return q;
    const toks = STRIP(String(q).toLowerCase()).match(/[a-z][a-z0-9-]*/g) || [];
    return toks.map(t => (t in dict) ? dict[t] : cognate(t, lang))
               .filter(Boolean).join(" ");
  }

  global.KF_I18N = { UI, detect, toEnglish, translateSentence, langs: ["en", "fr", "es", "ja"] };
})(window);
