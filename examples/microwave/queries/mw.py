import soidlib

start  = 0
cancel = 1
dopen  = 2
dclose = 3
nothng = 4


def introduction():
    return (
        f'\n\tcontext: Logs for an autonomous kitchen note that the automated microwave operator did not attempt to cancel a run'
        f'\n\t         on a microwave which was displaying an error. As a result, the microwave failed and damaged the facility.'
        f'\n\t                                                                                                                  '
        f'\n\t         Due to the resulting damage to the operator, it is unknown whether the sensors of the operator registered'
        f'\n\t         the error before the damage occurred, nor is it known what action the operator chose in the event that it'
        f'\n\t         was aware of the error. As such, the question is whether the operator could plausibly bear responsibility'
        f'\n\t         for not averting the failure, or whether it would have acted appropriately had the error been noticed in '
        f'\n\t         time. Our core question concerns the counterfactual:                                                     '
        f'\n\t                                                                                                                  '
        f'\n\t               error {soidlib.symbols.counterfactual} push cancel                                                 '
        f'\n\t                                                                                                                  '
        f'\n\t         However, note that of the five decisions the operator can choose -- to (i) cancel the run; (ii) open the '
        f'\n\t         door; (iii) close the door; (iv) push start; or (v) do nothing -- the choice to close the door could also'
        f'\n\t         be a reasonable action consistent with an attempt to resolve the error before any damage occurs. Closing '
        f'\n\t         the door when possible could resolve the error in and of itself, and at the very least could help contain'
        f'\n\t         any danger from the appliance. So we also consider the counterfactual:                                   '
        f'\n\t                                                                                                                  '
        f'\n\t               '

        f'( ( error {soidlib.symbols.land} door open ) {soidlib.symbols.counterfactual} close door ) {soidlib.symbols.implies} '
        f'( ( error {soidlib.symbols.land} door closed ) {soidlib.symbols.counterfactual} push cancel )'

        f'\n\t                                                                                                                  '
        f'\n\t         As such, we pose the following questions.                                                                '
        f'\n\t                                                                                                                  '
        f'\n\t         1. In the event of a recognized error, does the operator always decide to cancel the run?                '
        f'\n\t         2. In the event of ..., is there any scenario in which the operator decides to do nothing?               '
        f'\n\t         3. In the event of ..., is there any scenario in which the operator decides to open the door?            '
        f'\n\t         4. In the event of ..., does the operator always decide to either cancel the run or close the door?      '
        f'\n\t         5. In the event of ... with a closed door, does the operator always decide to cancel the run?            '
        f'\n\t         6. Is canceling a direct response to the error? Will the operator ever decide to cancel an errorless run?'
        f'\n\t                                                                                                                  '
        f'\n\t         Question (1) queries our counterfactual directly. Questions (2-3) clarify whether the operator could have'
        f'\n\t         either ignored the danger, or even contributed to it by opening the appliance door. Questions (4-5) ask  '
        f'\n\t         whether our allowance that the operator may choose first to close the door applies. If the operator might'
        f'\n\t         choose to close the door instead -- and once closed, it would then choose to push cancel -- its behavior '
        f'\n\t         we would consider to be consistent with an intention to cancel the run and resolve the error. Finally, in'
        f'\n\t         Question (6) we ask whether a decision to push cancel is actually responsive to the error, and not just a'
        f'\n\t         coincidence where the operator chooses it with an intention other than to resolve the error.             '
    )


def declare():

    E = { 'error'    : soidlib.types.bool( 'error' ),
          'close'    : soidlib.types.bool( 'close' ),
          'heat'     : soidlib.types.bool( 'heat'  ),
          'start'    : soidlib.types.bool( 'start' ) }

    S = { 'started'  : soidlib.types.bool( 'started' ) }

    P = { 'decision' : soidlib.types.u32( 'decision', pp = { '0' : 'push start',
                                                             '1' : 'push cancel',
                                                             '2' : 'open door',
                                                             '3' : 'close door',
                                                             '4' : 'do nothing'   } ) }

    return E, S, P
