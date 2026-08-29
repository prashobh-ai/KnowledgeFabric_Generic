"""Suggested demo questions, translated — French, Spanish, Japanese.

One entry per tenant slug, aligned index-for-index with the pack's English
`questions` tuple. Domain acronyms (MEL, AD, CARC, 837P, SOC 2, WCAG, MARPOL,
CAPA, EDI …) stay as written — that is how practitioners use them in every
one of these languages. The demo translates the QUERY and the ANSWER; source
documents stay English, which these questions retrieve against through the
client-side dictionary in site/assets/js/i18n.js.
"""

QUESTIONS_I18N: dict[str, dict[str, tuple[str, ...]]] = {
    "q-airlines": {
        "fr": (
            "Quel est le délai de réparation d'un élément MEL de catégorie B et qui approuve une prolongation ?",
            "Quels codes de retard sont attribués quand le dégivrage fait dépasser le créneau de départ ?",
            "Comment la légalité de l'équipage est-elle revérifiée pendant une reprise IROPS ?",
            "Que doit contenir le dispatch release avant que l'avion puisse repousser ?",
            "Quelles escales acceptent les marchandises dangereuses sans agent tiers ?",
        ),
        "es": (
            "¿Cuál es el plazo de reparación de un elemento MEL de categoría B y quién aprueba una extensión?",
            "¿Qué códigos de demora se asignan cuando el deshielo empuja una salida más allá de su slot?",
            "¿Cómo se reverifica la legalidad de la tripulación durante una recuperación IROPS?",
            "¿Qué debe constar en el dispatch release antes de que la aeronave pueda retroceder?",
            "¿Qué estaciones aceptan mercancías peligrosas sin un agente externo?",
        ),
        "ja": (
            "カテゴリーB のMEL項目の修復期限は何日で、延長は誰が承認しますか？",
            "防氷作業で出発がスロットを超過した場合、どの遅延コードが割り当てられますか？",
            "IROPS からの回復中、乗務員の法定要件はどのように再確認されますか？",
            "航空機がプッシュバックする前に、ディスパッチリリースには何が必要ですか？",
            "第三者代理店なしで危険物受託を扱えるのはどの空港ですか？",
        ),
    },
    "q-aerotech": {
        "fr": (
            "Quelles consignes de navigabilité sont ouvertes sur la structure de voilure et quels sont leurs intervalles récurrents ?",
            "Comment un constat non routinier devient-il un schéma de réparation approuvé ?",
            "Quelles preuves faut-il pour la traçabilité back-to-birth d'une pièce à vie limitée ?",
            "Qui peut signer un certificat de remise en service après un check C ?",
            "Quels service bulletins ont été différés et sur quel raisonnement de coût ?",
        ),
        "es": (
            "¿Qué directivas de aeronavegabilidad están abiertas sobre la estructura del ala y cuáles son sus intervalos recurrentes?",
            "¿Cómo un hallazgo no rutinario se convierte en un esquema de reparación aprobado?",
            "¿Qué evidencia se requiere para la trazabilidad back-to-birth de una pieza de vida limitada?",
            "¿Quién puede firmar un certificado de puesta en servicio tras un check C?",
            "¿Qué service bulletins se aplazaron y con qué justificación de coste?",
        ),
        "ja": (
            "主翼構造に対して未対応の耐空性改善命令はどれで、その反復間隔はどれくらいですか？",
            "非定常の指摘はどのようにして承認済みの修理方案になりますか？",
            "寿命管理部品の出生からの追跡には、どのような証拠が必要ですか？",
            "Cチェック後の耐空証明への署名は誰ができますか？",
            "どのサービスブルテンが延期され、そのコスト上の根拠は何でしたか？",
        ),
    },
    "q-health": {
        "fr": (
            "Quels order sets sont liés au parcours sepsis et qu'est-ce qui les déclenche ?",
            "Comment les médicaments à haut risque sont-ils vérifiés avant administration ?",
            "Quelles liaisons terminologiques l'interface de résultats utilise-t-elle pour les observations de laboratoire ?",
            "Quels facteurs contributifs reviennent le plus dans les événements de sécurité médicamenteuse ?",
            "Quand le present-on-admission doit-il être déterminé et qui décide ?",
        ),
        "es": (
            "¿Qué order sets están vinculados a la vía de sepsis y qué los activa?",
            "¿Cómo se verifican los medicamentos de alto riesgo antes de administrarlos?",
            "¿Qué vinculaciones terminológicas usa la interfaz de resultados para observaciones de laboratorio?",
            "¿Qué factores contribuyentes aparecen más en los eventos de seguridad de medicación?",
            "¿Cuándo debe determinarse el present-on-admission y quién lo decide?",
        ),
        "ja": (
            "敗血症パスに紐づくオーダーセットはどれで、何がそれらをトリガーしますか？",
            "ハイアラート薬は投与前にどのように確認されますか？",
            "検査結果インターフェースは臨床検査の観察値にどの用語バインディングを使いますか？",
            "投薬安全イベントで最も多い寄与要因は何ですか？",
            "present-on-admission はいつ判定し、誰が決定しますか？",
        ),
    },
    "q-assure-claims": {
        "fr": (
            "Quels codes CARC génèrent le plus de refus et quelle est la règle de retraitement pour chacun ?",
            "Quels critères cliniques s'appliquent à l'autorisation préalable d'imagerie avancée ?",
            "De combien de temps dispose un prestataire pour un appel de premier niveau ?",
            "Quelles boucles du 837P portent les données de coordination des prestations ?",
            "Qu'est-ce qui déclenche un contrôle d'intégrité de paiement sur le modificateur 25 ?",
        ),
        "es": (
            "¿Qué códigos CARC generan el mayor volumen de denegaciones y cuál es la regla de reprocesamiento de cada uno?",
            "¿Qué criterios clínicos aplican a la autorización previa de imagen avanzada?",
            "¿Cuánto tiempo tiene un proveedor para presentar una apelación de primer nivel?",
            "¿Qué loops del 837P llevan los datos de coordinación de beneficios?",
            "¿Qué activa una revisión de integridad de pagos sobre el modificador 25?",
        ),
        "ja": (
            "支払拒否件数が最も多い CARC コードはどれで、それぞれの再処理ルールは何ですか？",
            "高度画像診断の事前承認にはどの臨床基準が適用されますか？",
            "プロバイダーが第一次不服申立てを行える期限はどれくらいですか？",
            "837P のどのループが給付調整データを保持しますか？",
            "モディファイア 25 に対する支払適正性エディットは何がトリガーしますか？",
        ),
    },
    "q-pharma": {
        "fr": (
            "Qu'est-ce qui déclenche une investigation OOS de phase II et qui autorise le retest ?",
            "Comment l'impact lot est-il évalué quand une déviation de remplissage stérile est ouverte ?",
            "Quels CAPA restent ouverts au-delà de leur date de contrôle d'efficacité ?",
            "Quelles étapes du change control déterminent la déclarabilité réglementaire ?",
            "Comment les déviations de protocole sur les sites cliniques sont-elles escaladées ?",
        ),
        "es": (
            "¿Qué desencadena una investigación OOS de fase II y quién autoriza el reanálisis?",
            "¿Cómo se evalúa el impacto en el lote cuando se levanta una desviación de llenado estéril?",
            "¿Qué CAPA siguen abiertas más allá de su fecha de verificación de eficacia?",
            "¿Qué pasos del control de cambios determinan la reportabilidad regulatoria?",
            "¿Cómo se escalan las desviaciones de protocolo en los centros clínicos?",
        ),
        "ja": (
            "フェーズ II の規格外（OOS）調査は何がトリガーし、再試験は誰が承認しますか？",
            "無菌充填の逸脱が起票された場合、バッチへの影響はどのように評価されますか？",
            "有効性確認期日を過ぎても未クローズの CAPA はどれですか？",
            "変更管理のどのステップが規制当局への報告要否を決めますか？",
            "治験実施施設でのプロトコル逸脱はどのようにエスカレーションされますか？",
        ),
    },
    "q-devicelab": {
        "fr": (
            "Quelles design inputs n'ont aucun protocole de vérification lié ?",
            "Comment la déclarabilité est-elle décidée quand une réclamation allègue un préjudice patient ?",
            "Quels risques résiduels ont été acceptés sous ALARP et sur quelle base bénéfice ?",
            "Quels éléments logiciels sont de classe C et quels tests exigent-ils ?",
            "Comment un changement fournisseur alimente-t-il le dossier de gestion des risques ?",
        ),
        "es": (
            "¿Qué design inputs no tienen un protocolo de verificación vinculado?",
            "¿Cómo se decide la reportabilidad cuando una queja alega daño al paciente?",
            "¿Qué riesgos residuales se aceptaron bajo ALARP y con qué base de beneficio?",
            "¿Qué elementos de software son clase C y qué pruebas requieren?",
            "¿Cómo fluye un cambio de proveedor al archivo de gestión de riesgos?",
        ),
        "ja": (
            "検証プロトコルが紐づいていない設計インプットはどれですか？",
            "苦情が患者への危害を主張する場合、当局報告の要否はどう判断されますか？",
            "ALARP の下で受容された残留リスクはどれで、その便益上の根拠は何ですか？",
            "クラス C のソフトウェアアイテムはどれで、どのテストが必要ですか？",
            "サプライヤー変更はどのようにリスクマネジメントファイルへ反映されますか？",
        ),
    },
    "q-bank": {
        "fr": (
            "Qu'est-ce qui déclenche une vigilance renforcée sur une entreprise à forte intensité d'espèces ?",
            "Quelles covenants sont standard sur les facilités immobilières commerciales ?",
            "Comment les constats de validation de modèle sont-ils suivis jusqu'à clôture ?",
            "Quel est le chemin d'escalade quand une alerte de surveillance suggère du structuring ?",
            "Quelles notations de risque exigent l'approbation du comité de crédit plutôt qu'une délégation ?",
        ),
        "es": (
            "¿Qué desencadena la debida diligencia reforzada sobre un negocio intensivo en efectivo?",
            "¿Qué covenants son estándar en las facilidades de inmobiliario comercial?",
            "¿Cómo se siguen los hallazgos de validación de modelos hasta su cierre?",
            "¿Cuál es la ruta de escalado cuando una alerta de monitoreo sugiere estructuración?",
            "¿Qué calificaciones de riesgo exigen aprobación del comité de crédito en lugar de autoridad delegada?",
        ),
        "ja": (
            "現金集約型事業に対する厳格な顧客管理（EDD）は何がトリガーしますか？",
            "商業用不動産ファシリティで標準的なコベナンツはどれですか？",
            "モデル検証の指摘事項はどのようにクローズまで追跡されますか？",
            "取引モニタリングのアラートがストラクチャリングを示唆した場合のエスカレーション経路は？",
            "どのリスク格付が委任権限ではなく与信委員会の承認を要しますか？",
        ),
    },
    "q-assurance": {
        "fr": (
            "Comment la materialité de performance est-elle fixée par rapport à la materialité globale ?",
            "Quels risques significatifs exigent une réponse substantive quelle que soit la confiance dans les contrôles ?",
            "Que doit évaluer un engagement quality reviewer avant la publication du rapport ?",
            "Comment les exceptions de contrôle sont-elles évaluées en gravité ?",
            "Quels Trust Services Criteria sont dans le périmètre d'un SOC 2 couvrant la disponibilité ?",
        ),
        "es": (
            "¿Cómo se fija la materialidad de ejecución respecto a la materialidad global?",
            "¿Qué riesgos significativos exigen una respuesta sustantiva con independencia de la confianza en controles?",
            "¿Qué debe evaluar un revisor de calidad del encargo antes de emitir el informe?",
            "¿Cómo se evalúa la severidad de las excepciones de control?",
            "¿Qué Trust Services Criteria entran en alcance en un SOC 2 que cubre disponibilidad?",
        ),
        "ja": (
            "手続実施上の重要性は全体の重要性に対してどのように設定されますか？",
            "統制への依拠にかかわらず実証的対応を要する特別な検討を必要とするリスクはどれですか？",
            "報告書発行前に審査担当者（EQR)は何を評価しなければなりませんか？",
            "統制の例外事項の重大性はどのように評価されますか？",
            "可用性を対象とする SOC 2 では、どの Trust Services Criteria が範囲に入りますか？",
        ),
    },
    "q-cruise": {
        "fr": (
            "Quels codes de déficience Port State Control reviennent dans la flotte et quelles en sont les causes racines ?",
            "Quels temps d'exercice doivent être atteints et comment les écarts sont-ils escaladés ?",
            "Comment les registres d'halogénation de l'eau potable sont-ils vérifiés avant une inspection VSP ?",
            "Quels points de contingence sont fixés dans un plan de voyage pour une approche portuaire contrainte ?",
            "Quelles exigences de zone spéciale MARPOL changent les contrôles de rejet ?",
        ),
        "es": (
            "¿Qué códigos de deficiencia de Port State Control se repiten en la flota y cuáles son sus causas raíz?",
            "¿Qué tiempos de simulacro deben lograrse y cómo se escalan los incumplimientos?",
            "¿Cómo se verifican los registros de halogenación del agua potable antes de una inspección VSP?",
            "¿Qué puntos de contingencia se fijan en un plan de viaje para una aproximación portuaria restringida?",
            "¿Qué requisitos de zona especial MARPOL cambian los controles de descarga?",
        ),
        "ja": (
            "船隊で繰り返し発生しているポートステートコントロールの指摘コードはどれで、根本原因は何ですか？",
            "訓練で達成すべき所要時間は何分で、未達はどのようにエスカレーションされますか？",
            "VSP 検査の前に、飲料水のハロゲン処理記録はどのように検証されますか？",
            "制約のある入港アプローチでは、航海計画にどのコンティンジェンシーポイントを設定しますか？",
            "MARPOL 特別海域の要件は排出管理をどのように変えますか？",
        ),
    },
    "q-retail": {
        "fr": (
            "Quelles sont les exigences d'étiquetage carton et quelles pénalités s'appliquent en cas de manquement ?",
            "Comment le stock de sécurité est-il calculé pour les articles saisonniers ?",
            "Quelles transactions EDI un fournisseur doit-il certifier avant la première expédition ?",
            "Comment le sourcing ship-from-store choisit-il entre les nœuds ?",
            "Qu'est-ce qui déclenche une enquête d'inventaire tournant plutôt qu'un ajustement de routine ?",
        ),
        "es": (
            "¿Cuáles son los requisitos de etiquetado de cajas y qué contracargos aplican cuando se incumplen?",
            "¿Cómo se calcula el stock de seguridad para artículos de temporada?",
            "¿Qué transacciones EDI debe certificar un proveedor antes del primer envío?",
            "¿Cómo decide el sourcing ship-from-store entre nodos?",
            "¿Qué desencadena una investigación de conteo cíclico en lugar de un ajuste rutinario?",
        ),
        "ja": (
            "カートンラベリングの要件は何で、不備の場合どのチャージバックが適用されますか？",
            "季節商品の安全在庫はどのように計算されますか？",
            "初回出荷の前にベンダーが認証すべき EDI トランザクションはどれですか？",
            "ship-from-store のソーシングはノード間でどのように選択しますか？",
            "定期的な調整ではなくサイクルカウント調査をトリガーするのは何ですか？",
        ),
    },
    "q-quality": {
        "fr": (
            "Quels sont les critères de sortie du test système et qui peut y déroger ?",
            "Comment la sévérité d'un défaut se distingue-t-elle de la priorité pendant le triage ?",
            "Quels critères WCAG échouent le plus souvent et quel est le schéma de remédiation ?",
            "Quel modèle de charge la spécification de performance utilise-t-elle pour les pics d'activité ?",
            "Comment un quality gate décide-t-il de bloquer une release plutôt que d'avertir ?",
        ),
        "es": (
            "¿Cuáles son los criterios de salida de la prueba de sistema y quién puede eximirlos?",
            "¿Cómo se distingue la severidad de un defecto de la prioridad durante el triaje?",
            "¿Qué criterios WCAG fallan con más frecuencia y cuál es el patrón de remediación?",
            "¿Qué modelo de carga usa la especificación de rendimiento para los picos de actividad?",
            "¿Cómo decide un quality gate bloquear una release en lugar de advertir?",
        ),
        "ja": (
            "システムテストの終了基準は何で、その適用除外は誰が承認できますか？",
            "トリアージ中、不具合の重大度と優先度はどのように区別されますか？",
            "最も頻繁に不適合となる WCAG 達成基準はどれで、その是正パターンは何ですか？",
            "性能仕様はピーク時取引にどのワークロードモデルを使いますか？",
            "クオリティゲートは、警告ではなくリリースのブロックをどのように判断しますか？",
        ),
    },
}
