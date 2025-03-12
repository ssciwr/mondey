// This defines all the ids of text that should be provided in multiple languages.
// The text values here only provide default german placeholder values, mainly for convenience when developing the code.
// The actual text values are downloaded at runtime from the server, and are editable from the admin frontend.

export const translationIds = {
	milestone: {
		answer0Text: "Noch gar nicht",
		answer0Desc:
			"Das Kind macht noch keine Anstalten bzw. ist noch nicht in der Lage, das Verhalten auszuführen.",
		answer1Text: "In Ansätzen",
		answer1Desc:
			"Das Kind zeigt erste Ansätze, das Verhalten auszuführen, weicht dabei aber noch erheblich von der Beschreibung ab oder/und ist sehr unsicher.",
		answer2Text: "Weitgehend",
		answer2Desc:
			"Das Kind beherrscht das Verhalten im Prinzip, zeigt es aber erst selten, ist dabei  noch leicht unsicher oder führt es nicht ganz sauber aus.",
		answer3Text: "Zuverlässig",
		answer3Desc:
			"Das Kind zeigt das Verhalten mehrmals sicher und genau wie beschrieben.",
		milestones: "Meilensteine",
		observation: "Beobachtungshinweise",
		help: "Förderhilfen",
		info: "Information",
		next: "Weiter",
		prev: "Zurück",
		moreInfoOnLegend: "Mehr Info",
		autoNext: "Automatisch weiter",
		groupOverviewLabel: "Übersicht Meilensteingruppen",
		alertMessageRetrieving: "Fehler beim Abrufen der Meilensteine",
		alertMessageError: "Ein Fehler ist aufgetreten",
		submitImage: "Bild einreichen",
		submitImageText:
			"Haben Sie ein Bild von Ihrem Kind bei diesem Meilenstein, das Sie gerne beisteuern und veröffentlichen möchten? Wenn ja, können Sie es hier einreichen.",
		submitImageConditions:
			"Ich bin damit einverstanden, dass dieses Bild veröffentlicht und den Benutzern als eines der Meilensteinbilder auf dieser Website angezeigt wird, sofern es von den Site-Administratoren genehmigt wird.",
		recommendOk:
			"Das Kind hat für sämtliche Meilensteingruppen altergemäße Bewertungen erhalten.",
		recommendOkShort: "Alles im grünen Bereich!",
		recommendWatch:
			"Das Kind hat für einige Meilensteingruppen leicht unterdurchschnittliche Bewertungen erhalten.",
		recommendOkMs:
			"Das Kind hat für sämtliche Meilensteine altergemäße Bewertungen erhalten.",
		recommendWatchMs:
			"Das Kind hat für einige Meilensteine leicht unterdurchschnittliche Bewertungen erhalten.",
		recommendWatchShort: "Aufgepasst!",
		recommmendHelp:
			"Entwicklung des Kindes ist deutlich unterdurchschnittlich.",
		recommendHelpShort: "Enwicklungsverzögerung!",
		showHistory: "Feedback zu vorherigen Beobachtungszeiträumen anzeigen",
		moreInfoOnEval: "Mehr Informationen zur Bewertung",
		legend: "Erklärung zu den einzelnen Symbolen",
		selectFeedback: "Wählen sie nun zu welchem Zeitpunkt sie Feedback möchten",
		feedbackExplanation:
			"Das Feedback basiert auf einem Vergleich Ihrer Einschätzungen mit den Einschätzungen anderer Nutzer und folgt einer einfachen Regel:",
		feedbackExplanationDetailed:
			"Die Farben und Symbole zeigen an, ob das Kind altersgemäß entwickelt ist oder ob es in einzelnen Bereichen Unterstützung benötigt. Durch setzen des Hakens unten können sie vergangene Beobachtungszeiträume einsehen und so die Entwicklung des Kindes über einen längeren Zeitraum verfolgen. Es werden standardmäßig nur die Bewertungen der Meilensteingruppen angezeigt. Für eine genauere Analyse können sie die Bewertungen der einzelnen Meilensteine einsehen indem sie auf die jeweilige Meilensteingruppe klicken. Beachten sie bitte die zusätzlichen Informationen und die Erklärung zu den Symbolen.",
		feedbackDetailsMilestoneGroup:
			"Zu jeder Meilensteingruppe wird der Durchschnitt und die Standardabweichung der erreichten Punktzahl aller für das Kindesalter relevanten Meilensteine dieser Gruppe berechnet. Danach wird der Durchschnitt des der erreichten Punktzahl des Kindes mit dem Durchschnitt der Gruppe verglichen. Wenn der Durchschnitt des Kindes zwei Standardabweichungen unter dem Gruppendurchschnitt liegt, wird das Kind als 'Entwicklung verzögert' eingestuft (rot), wenn es zwei bis eine Standardabweichung unterhalb des Gruppendurchschnitts liegt, wird es als 'Entwicklung leicht verzögert' eingestuft (gelb). Wenn die Durchschnittszahl des Kindes innerhalb einer Standardabweichung des Gruppendurchschnitts oder darüber liegt, wird es als 'Entwicklung altersgemäß' eingestuft (grün). Statistisch liegen ungefähr 67% aller Kinder liegen innerhalb einer Standardabweichung um den Gruppendurchschnitt und 95% innerhalb von zwei Standardabweichungen. Zur Bewertung dieser Einstufungen ist es sinnvoll, die Bewertung der einzelnen Meilensteine miteinzubeziehen",
		feedbackDetailsMilestone:
			"Einzelne Meilensteine werden nach demselben Schema bewertet, allerdings sind hier Durchschnitt und Standardabweichung für den jeweiligen Meilenstein relevant. Beachten sie, dass die Bewertung einzelner Meilensteine nicht diesselbe sein muss wie für die ganze Gruppe - einzelne Meilensteine können gegebenenfalls signifikant verzögert sein ohne dass die ganze Meilensteingruppe als entwicklungsverzögert bewertet wird. In solchen Fällen ist besondere Aufmerksamkeit notwendig.",
		disableHelp: "Ausblenden",
		noFeedback:
			"Kein Feedback verfügbar. Sie müssen ein Kind länger als eine Woche beobachten und regelmäßig Meilensteine bewerten um Feedback zu erhalten.",
		current: "Aktuell",
		toTheMilestone: "Zum Meilenstein",
		older: "Weiter zurück",
		newer: "Weiter vor",
		notEnoughDataYet: "Noch nicht genügend Daten für Feedback",
		summaryScore: "Gesamtergebnis:",
		printReport: "Protokol drucken",
		timeperiod: "Zeitraum",
		born: "Geboren (Monat)",
		child: "Kind",
		date: "Datum",
		reportTitle: "Entwicklungsbericht",
	},
	search: {
		allLabel: "Alle",
		allPlaceholder: "Alle Kategorien durchsuchen",
		nameLabel: "Name",
		namePlaceholder: "Nach Namen suchen",
		remarkLabel: "Bemerkung",
		remarkPlaceholder: "Nach Bemerkungen suchen",
		descriptionLabel: "Beschreibung",
		descriptionPlaceholder: "Nach Beschreibungen suchen",
		surveyLabel: "Titel",
		surveyPlaceholder: "Nach Titel durchsuchen",
		statusLabel: "Status",
		statusPlaceholder: "Nach Status suchen",
		milestoneLabel: "Meilenstein",
		milestonePlaceholder: "Nach enthaltenem Meilenstein durchsuchen",
		complete: "fertig",
		incomplete: "unfertig",
	},
	admin: {
		label: "Administration",
		title: "Titel",
		languages: "Sprachen",
		milestone: "Meilenstein",
		milestones: "Meilensteine",
		milestoneGroups: "Meilensteingruppen",
		translations: "Übersetzungen",
		users: "Benutzer",
		userQuestions: "Fragen über Beobachter",
		childQuestions: "Fragen über Kind",
		question: "Frage",
		selectOptions: "Optionen",
		actions: "Aktionen",
		selectPlaceholder: "Erstens,Zweitens,Drittens;",
		add: "Hinzufügen",
		approve: "Genehmigen",
		edit: "Bearbeiten",
		delete: "Löschen",
		reorder: "Neu ordnen",
		deleteAreYouSure: "Möchten Sie dies wirklich löschen?",
		yesSure: "Ja, ich bin sicher",
		noCancel: "Nein, abbrechen",
		saveChanges: "Änderungen speichern",
		cancel: "Abbrechen",
		desc: "Beschreibung",
		obs: "Beobachtungshinweise",
		help: "Förderhilfen",
		image: "Bild",
		images: "Bilder",
		submittedImages: "Eingereichte Bilder",
		age: "Alter",
		averageScore: "Durchschnittspunktzahl",
		viewData: "Daten anzeigen",
		expectedAge: "Voraussichtliches Alter",
		recalculateExpectedAge: "Voraussichtliches Alter neu berechnen",
		newExpectedAge: "Neues Voraussichtliches Alter",
		editUserQuestionTitle: "Frage an Benutzer editieren",
		expectedAgeData: "Voraussichtliches Alter Daten",
		maxFileSizeIs: "Die maximale Dateigröße für ein Bild beträgt",
	},
	researcher: {
		label: "Wissenschaft",
		images: "Bilder",
	},
	registration: {
		heading: "Als neuer Benutzer registrieren",
		alertMessageMissing: "Bitte füllen Sie alle Felder aus.",
		alertMessageError: "Ein Fehler ist aufgetreten",
		alertMessagePasswords: "Passwörter stimmen nicht überein",
		alertMessageTitle: "Fehler",
		usernameLabel: "Benutzername",
		passwordLabel: "Passwort",
		emailLabel: "E-Mail",
		passwordConfirmLabel: "Passwort wiederholen",
		researchCode: "Forschungscode (optional)",
		submitButtonLabel: "Absenden",
		selectPlaceholder: "Bitte auswählen",
		successMessage: "Bitte überprüfen sie ihr E-Mail Postfach",
		emailValidationMessage:
			"Ihre E-Mail-Adresse wurde bestätigt und Sie können sich jetzt anmelden.",
		emailValidationError:
			"Ungültiger oder abgelaufener E-Mail-Validierungslink",
		goHome: "Zur Hauptseite",
	},
	login: {
		heading: "Einloggen",
		alreadyLoggedInMessage:
			"Sie sind bereits angemeldet. Melden sie sich zuerst ab um den Account zu wechseln.",
		alertMessageTitle: "Fehler",
		badCredentials: "Ungültige E-Mail-Adresse oder ungültiges Passwort",
		badActiveUser: "Der Benutzer konnte nicht gefunden werden",
		notLoggedIn: "Bitte melden sie sich erneut an",
		unauthorized: "Zugang verweigert",
		notRegistered: "Noch nicht registriert?",
		usernameLabel: "Benutzerkennung",
		passwordLabel: "Passwort",
		role: "Rolle",
		observerRole: "Beobachter",
		researcherRole: "Wissenschaftler",
		adminRole: "Admin",
		submitButtonLabel: "Absenden",
		selectPlaceholder: "Bitte auswählen",
		profileButtonLabelDefault: "Einloggen",
		profileButtonLabelLogout: "Logout",
		profileTitleDefault: "Willkommen!",
		profileAccess: "Ihr Profil",
		registerNew: "Als neuer Benutzer registrieren",
		forgotPassword: "Passwort vergessen?",
	},
	userData: {
		label: "Persönliche Daten",
		heading: "Benutzerdaten eingeben",
		alertMessageTitle: "Fehler",
		alertMessageMissing:
			"Bitte füllen Sie die benötigten Felder (hervorgehoben) aus.",
		alertMessageUserNotFound:
			"Kein aktiver Benutzer. Bitte loggen sie sich erneut ein",
		alertMessageError:
			"Ein Fehler ist aufgetreten. Bitte versuchen sie es später erneut.",
		alertMessageUpdate: "Bitte aktualisieren sie ihre Eingaben",
		submitButtonLabel: "Abschließen",
		changeData: "Daten vollständig, zum bearbeiten klicken",
		loadingMessage: "Daten werden geladen",
		settingsLabel: "Einstellungen",
	},
	settings: {
		settings: "Einstellungen",
		changePassword: "Passwort ändern",
		enterPassword: "Bitte aktuelles Passwort eingeben",
		getUserError: "kein aktiver Benutzer",
		oldPasswordWrong: "Das angegbene Passwort ist falsch",
		newPassword: "Bitte neues Passwort",
		newPasswordConfirm: "Bitte neues Passwort bestätigen",
		confirmChange: "Änderungen bestätigen",
		confirmPasswordChangeSuccess: "Änderung des Passworts erfolgreich",
		emptyPasswordError: "Das Passwort darf nicht leer sein",
		nonMatchingPasswordsError: "Passwörter stimmen nicht überein",
		samePasswordsError: "Das neue Passwort darf nicht dem alten entsprechen",
		closeWindow: "Fenster schließen",
		sendError: "Beim Senden der Daten ist ein Fehler aufgetreten",
		defaultAlertMessage: "Ein Fehler ist aufgetreten",
		alertTitle: "Fehler",
		placeholder: "Bitte ausfüllen",
	},
	childData: {
		newChildHeading: "Neu",
		newChildHeadingLong: "Neues Kind registrieren",
		overviewLabel: "Kinder",
		overviewSummary:
			"Wählen sie ein Kind zur Beobachtung aus oder legen melden sie ein neues Kind an.",
		alertMessageMissing:
			"Bitte füllen Sie die benötigten Felder (hervorgehoben) aus.",
		alertMessageUserNotFound:
			"Kein aktiver Benutzer. Bitte loggen sie sich erneut ein",
		alertMessageError:
			"Ein Fehler ist aufgetreten. Bitte versuchen sie es später erneut.",
		alertMessageUpdate: "Bitte aktualisieren sie ihre Eingaben",
		alertMessageCreate: "Fehler beim Anlegen des Kindes",
		alertMessageRetrieving: "Fehler beim Anlegen des Kindes",
		alertMessageImage: "Fehler beim Bild download",
		alertMessageTitle: "Fehler",
		submitButtonLabel: "Abschließen",
		deleteButtonLabel: "Kind löschen",
		changeData: "Daten vollständig, zum bearbeiten klicken",
		loadingMessage: "Daten werden geladen",
		searchAllLabel: "Alle",
		searchAllPlaceholder: "Alle Kategorien durchsuchen",
		searchNameLabel: "Name",
		searchNamePlaceholder: "Kinder nach Namen durchsuchen",
		searchRemarkLabel: "Bemerkung",
		searchRemarkPlaceholder: "Bemerkungen zu Kindern durchsuchen",
		pleaseEnter: "Bitte eintragen",
		pleaseEnterNumber: "Bitte als Zahl eintragen",
		childName: "Name des Kindes?",
		childBirthYear: "Geburtsjahr des Kindes?",
		childBirthMonth: "Geburtsmonat des Kindes?",
		imageOfChildNew: "Neues Bild des Kindes hochladen (optional)",
		imageOfChildChange: "Bild des Kindes ändern (optional)",
		imageOfChildChangeDelete: "Das aktuelle Bild wurde gelöscht",
		noFileChosen: "Keine Datei ausgewählt",
		deleteImageButton: "Bild löschen",
		nextButtonLabel: "Weiter zu Meilensteinen",
		childColor: "Hintergrundfarbe für Icon wählen",
		chooseColor: "Farbe wählen",
		feedbackButtonLabel: "Feedback zur Entwicklung",
	},
	forgotPw: {
		heading: "Passwort vergessen?",
		resetHeading: "Passwort zurücksetzen",
		placeholder:
			"Bitte geben sie eine E-mail Adresse an um ihr Passwort zu erneuern",
		success: "Bitte überprüfen sie ihr E-Mail Postfach!",
		successReset: "Ihr Passwort wurde erfolgreich zurückgesetzt",
		goToLogin: "Zurück zum Login",
		pending: "Absenden",
		alertTitle: "Fehler",
		formatError: "Die angegebene email Adresse hat ein falsches Format",
		sendError:
			"Beim Senden der Daten ist ein Fehler aufgetreten. Bitte versuchen sie es erneut",
		confirmError: "Eingaben nicht identisch",
		error: "Ein Fehler ist aufgetreten",
		codeError: "Ungültiger oder leerer reset code",
		inputlabelPw: "Neues Passwort",
		inputlabelPwConfirm: "Neues Passwort bestätigen",
	},
	misc: {
		understood: "Verstanden",
		latest: "Aktuelles",
		downloads: "Downloads",
		contact: "Kontakt",
	},
	frontpage: {
		heading: "Möchten Sie die Entwicklung von Kindern begleiten und fördern?",
		summary: "Hier sind Sie genau richtig!",
		buttonLabel: "Anmeldung",
		toolTip: "Anmelden oder ein neues Konto erstellen",
	},
	frontpageAbout: {
		heading: "Was ist MONDEY?",
		summary1:
			"Ein mit Eltern und Fachkräften entwickeltes, wissenschaftlich geprüftes Program zur Beobachtung und Dokumentation der Entwicklung von Kindern bis 6 Jahre.",
		summary2:
			"Sie bewerten, wie gut das Kind bestimmte Alltagshandlungen ausführen kann. Auf dieser Basis bietet MONDEY Ihnen Feedback zum Entwicklungsstand des Kindes.",
		alt: "Ein kleines Kind hält ein Gänseblümchen in der Hand",
	},
	frontpageBookmarks: {
		title: "Welche Entwicklungsbereiche werden erfasst?",
		headingMotor: "Grobmotorik",
		headingFineMotor: "Handmotorik",
		headingThinking: "Denken",
		headingLanguage: "Sprache",
		headingSocialDevelopment: "Soziale Entwicklung",
		headingInnerStates: "Innere Zustände",
		headingSchool: "Schulische Vorläuferfertigkeiten",
		summaryMotor:
			"Verfolgen Sie, wie das Kind von seiner Geburt bis zum 6. Lebensjahr lernt, seinen Rumpf, seine Arme und seine Beine immer besser zu koordinieren und im Alltag immer komplexere Bewegungsmuster ausführt.",
		summaryFineMotor:
			"Beobachten Sie, wie das Kind lernt, seine Hände und Finger immer geschickter zu nutzen, um damit seine Umwelt zu erkunden und zu verändern.",
		summaryThinking:
			"Das Denken besteht aus Basisprozessen (z.B. wahrnehmen, vergleichen und kategorisieren, sich etwas merken, flexibel umschalten, in Symbolen denken) und aus höheren Prozessen (z.B. planen, analysieren, kreativ sein). Beobachten Sie, wie sich der kindliche Geist entfaltet.",
		summaryLanguage:
			"Zur Sprache gehören das Erkennen und Produzieren von Lauten, Worten und Sätzen. Entdecken Sie, wie das Kind andere Menschen versteht und lernt, sich ihnen verständlich zu machen.",
		summarySocialDevelopment:
			"Verfolgen Sie mit, wie Kinder das Verhalten anderer Menschen zunehmend besser verstehen und darauf Einfluss darauf nehmen, aber auch, wie sie lernen, sich in die Gemeinschaft einzufügen. Diese Entwicklung beginnt schon bei den Kleinsten, aber sie ist auch im Erwachsenenalter nie endgültig abgeschlossen...",
		summaryInnerStates:
			"Hier beobachten Sie, wie das Kind die Fähigkeit entwickelt, mit seinen Bedürfnissen, motivationalen Zuständen und mit seinen Gefühlen umzugehen. Einige Meilensteine dieses Bereiches sind erfahrungsgemäß nicht so einfach zu bewerten.",
		summarySchool:
			"Bei älteren Kindergarten- und Vorschulkindern lohnt es sich, genau hinzuschauen, welche geistigen und motorischen Fähigkeiten, die konkret auf die Schule vorbereiten, schon entwickelt wurden.",
	},
	footer: {
		contact: "Kontakt",
		information: "Informationen",
		research: "Forschung",
		imprint: "Presse und Medien",
		privacy: "Datenschutzerklärung",
		bottom: "Psychologisches Institut Heidelberg",
	},
	frontpageAccordion: {
		heading1: "Wie funktioniert MONDEY?",
		summary1:
			"<p>Für alle wichtigen Bereiche der Entwicklung bis zum Schulalter haben wir eine Liste von <strong>Meilensteine</strong> zusammengestellt. Jeder Meilenstein steht für eine Kompetenz, die KInder typischerweise irgendwann zwischen 0 und 6 Jahren erreichen. Meilensteine können Sie ohne besondere Ausbildung oder Testmaterial im Alltag gut beobachten und gezielt fördern. Gerne können Sie sich die Liste der Meilensteine vorab anschauen oder herunterladen.<br /><br />Wenn Sie sich anmelden, bitten wir Sie zunächst um einige <strong>Angaben zu Ihrer Person und zum beobachteten Kind</strong>. Diese Information benötigen wir ausschließlich, um ihre Daten richtig einordnen zu können und unsere Stichprobe in wissenschaftlichen Publikationen korrekt beschreiben zu können.<br /><br />Gerne können Sie sich die Liste der Personenbezogenen Daten vorab anschauen oder herunterladen, nach denen wir Sie fragen werden.<br /><br />Anschließend sollen Sie für jeden Entwicklungsbereich alle Meilensteine bewerten, indem Sie beurteilen, ob das Kind die beschriebene Kompetenz:<br /><ul><li>„noch nicht“,</li><li>„in Ansätzen“,</li>\n  <li>„weitgehend“</li><li>oder „zuverlässig“ zeigt.</li></ul><br /><br />Für die Bewertung jedes Meilensteins gibt es zur Unterstützung abrufbare <strong>Beobachtungshinweise</strong>.<br /><br />Bei der ersten <strong>Bestandsaufnahme</strong> werden Sie zunächst durch alle Meilensteine geführt. Je nach Alter des KIndes dauert das etwas länger. Wenn Sie die Entwicklung des gleichen KIndes später <strong>kontinuierlich weiter dokumentiere</strong> möchten, werden nur noch die Meilensteine abgefragt, die zuvor noch nicht als „zuverlässig gekonnt“ bewertet wurden.<br /><br />Am Ende Ihrer Bestandsaufnahme erhalten Sie ein <strong>Ampel-Feedback</strong>. Wir geben Ihnen für jeden Entwicklungsbereich einzeln Rückmeldung, ob das Kind:<br /><ul><li>altergemäß entwickelt ist (Ampel grün),</li><li>ob einzelne Meilensteine verspätet sind (Ampel gelb),</li><li>oder ob in einem Bereich Anzeichen für eine deutlich verzögerte Entwicklung gibt (Ampel rot).</li>\n</ul>\nDas Feedback basiert auf einem Vergleich mit einer großen Standard-Stichprobe. Auch Ihre Daten gehen in diese Vergleichsstichprobe ein. Sie wächst damit ständig und wird immer zuverlässiger.<br /><br />Zusätzlich erhalten Sie auf Wunsch auch Meilenstein-bezogene <strong>Förder-Hinweise</strong>.<br /><br />Wichtig ist, dass Sie Ihre Beobachtung in regelmäßigen Abständen vornehmen, um feststellen zu können, ob sich Änderungen am Entwicklungsstatus ergeben.<br />\nJedes Kind hat sein eigenes Tempo - vieles kann sich schnell ändern.<br /><br /><strong>Mit MONDEY lernen Sie:</strong><ul><li>die Entwicklungsfortschritte von Kindern kontinuierlich genau zu beobachten</li><li>die Kinder beim Erwerb wichtiger neuer Kompetenzen gezielt zu unterstützen</li><li>den Entwicklungsstand eines Kindes einzuschätzen und ggf. rechtzeitig Unterstützung zu geben</li></ul>Außerdem leisten Sie einen wichtigen Beitrag zur Entwicklungspsychologischen Grundlagenforschung!</p>",
		heading2: "Häufig gestellte Fragen",
		summary2:
			"Ein mit Eltern und Fachkräften entwickeltes, wissenschaftlich geprüftes Program zur Beobachtung und Dokumentation der Entwicklung von Kindern bis 6 Jahre. Sie bewerten, wie gut das Kind bestimmte Alltagshandlungen ausführen kann.",
	},
};
